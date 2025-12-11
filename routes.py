import os
import shutil
from flask import render_template, request, redirect, url_for, flash, session, Blueprint
from werkzeug.utils import secure_filename

from services import document_processor, ats_analyzer, interview_manager, llm_chains
from config import Config
from langchain_google_genai import ChatGoogleGenerativeAI # Only for initial LLM test

main_bp = Blueprint('main', __name__)

# Global variables for caching (same as before but managed through service layer)
global_jd_text = ""
global_resume_content = ""

# --- Helper Functions (moved from app.py, specific to routes or common) ---
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

@main_bp.route('/')
def index():
    llm_test_response = "LLM Test Not Run Yet."
    try:
        # Create a temporary LLM instance for this test only
        test_llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=Config.GOOGLE_API_KEY)
        test_prompt = "Hello, tell me something interesting about Python in one sentence."
        response = test_llm.invoke(test_prompt)
        llm_test_response = f"LLM Test Successful! Response: {response.content[:70]}..."
        print(llm_test_response)
    except Exception as e:
        llm_test_response = f"LLM Test Failed: {e}"
        print(f"LLM Test Failed: {e}")

    return render_template('index.html', llm_test_response=llm_test_response)


@main_bp.route('/upload_documents', methods=['GET', 'POST'])
def upload_documents():
    global global_jd_text, global_resume_content

    if request.method == 'POST':
        resume_file = request.files.get('resume')
        jd_text = request.form.get('job_description_text')

        if not resume_file or resume_file.filename == '':
            flash('Resume file is required.', 'danger')
            return redirect(request.url)
        if not allowed_file(resume_file.filename):
            flash('Only PDF and DOCX files are allowed for Resume.', 'danger')
            return redirect(request.url)
        
        if not jd_text or not jd_text.strip():
            flash('Job Description text cannot be empty.', 'danger')
            return redirect(request.url)

        try:
            # --- Process Resume File ---
            resume_filename = secure_filename(resume_file.filename)
            resume_filepath = os.path.join(Config.UPLOAD_FOLDER, resume_filename)
            resume_file.save(resume_filepath)
            resume_chunks = document_processor.load_and_split_file_document(resume_filepath)
            global_resume_content = "\n".join([c.page_content for c in resume_chunks])

            # --- Process JD Text ---
            global_jd_text = jd_text
            jd_chunks = document_processor.process_text_to_chunks(jd_text)

            all_chunks = resume_chunks + jd_chunks

            print("\n--- Combined Chunks (First 3) ---")
            for i, chunk in enumerate(all_chunks[:3]):
                print(f"Chunk {i+1}:\n{chunk.page_content[:200]}...\n")

            # --- ChromaDB Processing ---
            document_processor.initialize_vector_db(all_chunks, Config.CHROMA_DB_DIR)

            # --- ATS Score & Missing Keywords Calculation ---
            print("\n--- Calculating ATS Score and Keywords ---")
            jd_keywords = ats_analyzer.get_jd_keywords(global_jd_text)
            ats_score, ats_rationale = ats_analyzer.calculate_ats_score(global_resume_content, global_jd_text, jd_keywords)
            missing_keywords = ats_analyzer.get_missing_keywords(global_resume_content, jd_keywords)

            session['ats_results'] = {
                'score': ats_score,
                'rationale': ats_rationale,
                'jd_keywords': jd_keywords,
                'missing_keywords': missing_keywords
            }
            print(f"ATS Score: {ats_score}/100")
            print(f"Missing Keywords: {missing_keywords}")

            # --- Initialize Interview State ---
            session['current_stage'] = 'FOUNDATIONAL_WARMUP' # Start with warm-up
            session['stage_question_count'] = 0
            session['max_foundational_questions'] = Config.MAX_FOUNDATIONAL_QUESTIONS

            # Generate the very first question based on the initial warm-up prompt
            initial_question_generator_chain = llm_chains.get_initial_question_chain()
            
            initial_question_input = {
                "job_role": Config.JOB_ROLE,
                "jd_context": global_jd_text,
                "resume_context": global_resume_content 
            }
            initial_question = initial_question_generator_chain.invoke(initial_question_input)
            
            interview_history = [{"question": initial_question, "answer": None, "feedback": None}]
            session['interview_history'] = interview_history

            flash('Documents uploaded, processed, and analyzed successfully! Review your ATS score and keywords below.', 'success')
            return redirect(url_for('main.upload_documents')) # Redirect back to show ATS results

        except Exception as e:
            flash(f'Error processing files: {e}', 'danger')
            print(f"Error during file processing: {e}")
            return redirect(request.url)

    ats_results = session.get('ats_results')
    return render_template('upload_documents.html', ats_results=ats_results)


@main_bp.route('/start_interview')
def start_interview():
    current_interview_history = session.get('interview_history', [])
    
    if document_processor.get_vector_store() is None or not current_interview_history:
        flash("Please upload documents first to start the interview.", "warning")
        return redirect(url_for('main.upload_documents'))
    
    current_question = current_interview_history[-1]["question"]
    current_stage = session.get('current_stage', 'Unknown') 

    return render_template('interview.html', question=current_question, interview_history=current_interview_history, current_stage=current_stage)


@main_bp.route('/interview_flow', methods=['POST'])
def interview_flow():
    global global_jd_text, global_resume_content

    interview_history = session.get('interview_history', [])
    if not interview_history:
        flash("Interview session lost. Please upload documents again.", "danger")
        return redirect(url_for('main.upload_documents'))

    if document_processor.get_vector_store() is None:
        flash("Interview setup incomplete. Please upload documents.", "danger")
        return redirect(url_for('main.upload_documents'))

    user_answer = request.form.get('user_answer')
    if not user_answer:
        flash("Please provide an answer to continue.", "warning")
        return render_template('interview.html', question=interview_history[-1]["question"], interview_history=interview_history)

    if interview_history and interview_history[-1]["answer"] is None:
        interview_history[-1]["answer"] = user_answer
    
    formatted_chat_history = ""
    for entry in interview_history:
        if entry["question"]:
            formatted_chat_history += f"Interviewer: {entry['question']}\n"
        if entry["answer"]:
            formatted_chat_history += f"Candidate: {entry['answer']}\n"

    # --- Analyze the user's answer and get feedback/action ---
    last_question = interview_history[-1]["question"]
    feedback, next_action_type = interview_manager.analyze_and_feedback_answer(
        last_question,
        user_answer,
        global_jd_text,
        global_resume_content,
        formatted_chat_history
    )
    
    interview_history[-1]["feedback"] = feedback
    session['interview_history'] = interview_history

    print(f"\n--- Answer Analysis ---\nFeedback: {feedback}\nNext Action: {next_action_type}")

    # --- Handle END_INTERVIEW action immediately ---
    if next_action_type == "END_INTERVIEW":
        flash(f"Interview Concluded: {feedback}", "info")
        return redirect(url_for('main.end_interview'))
    
    # Update interview stage and question count
    interview_manager.update_interview_stage(next_action_type)

    # Get the next question based on analysis and current stage
    next_question, _ = interview_manager.get_next_question(
        next_action_type,
        global_jd_text,
        global_resume_content,
        formatted_chat_history
    )
    
    # Add the new question to history
    interview_history.append({"question": next_question, "answer": None, "feedback": None})
    session['interview_history'] = interview_history

    return redirect(url_for('main.start_interview'))


@main_bp.route('/end_interview')
def end_interview():
    """Clears the interview session and redirects to the upload page."""
    session.pop('interview_history', None)
    session.pop('ats_results', None)
    session.pop('current_stage', None)
    session.pop('stage_question_count', None)
    session.pop('max_foundational_questions', None)
    
    global global_jd_text, global_resume_content 
    global_jd_text = ""
    global_resume_content = ""

    document_processor.clear_vector_db(Config.CHROMA_DB_DIR)

    flash("Interview ended. Please upload new documents to start a new session.", "info")
    return redirect(url_for('main.upload_documents'))


@main_bp.route('/coding_challenge')
def coding_challenge():
    """Display coding challenge page"""
    from services import problems
    
    # Get problem from session or select a random one
    problem_id = session.get('current_problem_id')
    
    if problem_id:
        problem = problems.get_problem(problem_id)
    else:
        problem = problems.get_random_problem()
        session['current_problem_id'] = problem['id']
    
    if not problem:
        flash("Problem not found", "danger")
        return redirect(url_for('main.start_interview'))
    
    return render_template('coding_challenge.html', problem=problem)


@main_bp.route('/run_code', methods=['POST'])
def run_code():
    """Run code with sample test cases"""
    from services.code_executor import CodeExecutor, CodeExecutionError
    from services import problems
    import json as json_module
    
    data = request.get_json()
    code = data.get('code')
    language = data.get('language')
    problem_id = data.get('problem_id')
    
    if not code or not language:
        return json_module.dumps({'error': 'Missing code or language'}), 400
    
    executor = CodeExecutor()
    
    try:
        # Get problem test cases
        problem = problems.get_problem(problem_id)
        if not problem:
            return json_module.dumps({'error': 'Problem not found'}), 404
        
        # Run with first example test case
        test_case = problem['test_cases'][0]
        stdin_data = '\n'.join(test_case['input'])
        
        result = executor.execute(code, language, stdin_data)
        
        return json_module.dumps({
            'output': result['output'],
            'error': result.get('error'),
            'test_input': stdin_data
        })
        
    except CodeExecutionError as e:
        return json_module.dumps({'error': str(e)})
    except Exception as e:
        return json_module.dumps({'error': f'Unexpected error: {str(e)}'})
    finally:
        executor.cleanup()


@main_bp.route('/submit_code', methods=['POST'])
def submit_code():
    """Submit code and run all test cases"""
    from services.code_executor import CodeExecutor, CodeExecutionError
    from services import problems
    import json as json_module
    
    data = request.get_json()
    code = data.get('code')
    language = data.get('language')
    problem_id = data.get('problem_id')
    time_taken = data.get('time_taken', 0)
    
    if not code or not language:
        return json_module.dumps({'error': 'Missing code or language'}), 400
    
    executor = CodeExecutor()
    
    try:
        # Get problem
        problem = problems.get_problem(problem_id)
        if not problem:
            return json_module.dumps({'error': 'Problem not found'}), 404
        
        # Run all test cases
        test_results = []
        all_passed = True
        
        for test_case in problem['test_cases']:
            stdin_data = '\n'.join(test_case['input'])
            expected = test_case['expected_output'].strip()
            
            try:
                result = executor.execute(code, language, stdin_data)
                actual = result['output'].strip()
                
                # Normalize output for comparison
                actual_normalized = actual.replace(' ', '').replace('\n', '')
                expected_normalized = expected.replace(' ', '').replace('\n', '')
                
                passed = actual_normalized == expected_normalized
                
                test_results.append({
                    'input': stdin_data,
                    'expected': expected,
                    'actual': actual,
                    'passed': passed
                })
                
                if not passed:
                    all_passed = False
                    
            except CodeExecutionError as e:
                test_results.append({
                    'input': stdin_data,
                    'expected': expected,
                    'actual': f'Error: {str(e)}',
                    'passed': False
                })
                all_passed = False
        
        # Store submission in session
        if 'code_submissions' not in session:
            session['code_submissions'] = []
        
        session['code_submissions'].append({
            'problem_id': problem_id,
            'language': language,
            'passed': all_passed,
            'time_taken': time_taken
        })
        
        return json_module.dumps({
            'test_results': test_results,
            'all_passed': all_passed,
            'total_tests': len(test_results),
            'passed_tests': sum(1 for t in test_results if t['passed'])
        })
        
    except CodeExecutionError as e:
        return json_module.dumps({'error': str(e)})
    except Exception as e:
        return json_module.dumps({'error': f'Unexpected error: {str(e)}'})
    finally:
        executor.cleanup()


@main_bp.route('/change_problem/<int:problem_id>')
def change_problem(problem_id):
    """Change to a different problem"""
    from services import problems
    
    problem = problems.get_problem(problem_id)
    if problem:
        session['current_problem_id'] = problem_id
        flash(f'Switched to problem: {problem["title"]}', 'success')
    else:
        flash('Problem not found', 'danger')
    
    return redirect(url_for('main.coding_challenge'))