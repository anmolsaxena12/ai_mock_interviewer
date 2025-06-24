import os
import shutil
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
import re

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, SystemMessage

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import Docx2txtLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("FLASK_SECRET_KEY",
                                     "a_long_random_fallback_secret_key_if_env_not_loaded_PLEASE_CHANGE_ME")
if app.config['SECRET_KEY'] == "a_long_random_fallback_secret_key_if_env_not_loaded_PLEASE_CHANGE_ME":
    print(
        "WARNING: FLASK_SECRET_KEY not set in .env. Using a default. Please set a strong, random key in your .env for production!")

UPLOAD_FOLDER = 'uploads'
CHROMA_DB_DIR = 'chroma_db'
ALLOWED_EXTENSIONS = {'pdf', 'docx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure necessary folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CHROMA_DB_DIR, exist_ok=True)

# --- Global Variables for LLM, Embeddings, and Vector Store ---
google_api_key = os.getenv("GOOGLE_API_KEY")
if not google_api_key:
    raise ValueError("GOOGLE_API_KEY not found in .env file. Please set it.")

llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=google_api_key)

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

db = None
retriever = None
question_generator_chain = None  # This will now be context-dependent
global_jd_text = ""
global_resume_content = ""


# --- Helper Functions (Existing) ---
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def load_and_split_file_document(filepath):
    """Loads a document (PDF/DOCX) from a file and splits it into chunks."""
    if filepath.endswith('.pdf'):
        loader = PyPDFLoader(filepath)
    elif filepath.endswith('.docx'):
        loader = Docx2txtLoader(filepath)
    else:
        raise ValueError("Unsupported file type")

    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_documents(documents)
    return chunks


def process_text_to_chunks(text_content, source="Job Description"):
    """Converts raw text content into LangChain Documents and splits them."""
    if not text_content or not text_content.strip():
        return []

    doc = Document(page_content=text_content, metadata={'source': source})
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_documents([doc])
    return chunks


# --- ATS & KEYWORD HELPER FUNCTIONS ---

def get_jd_keywords(jd_text):
    """Uses LLM to extract key skills and requirements from the Job Description."""
    keyword_extraction_prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessage(
                "You are an expert HR assistant. Your task is to identify and list "
                "the most important technical skills, tools, programming languages, methodologies, "
                "and core requirements mentioned in the job description. "
                "List them as a comma-separated string, prioritize single words or short phrases. "
                "Exclude common words like 'experience', 'ability', 'strong', 'good communication', 'team player', 'responsible', 'collaborate'. "
                "Example: Python, SQL, AWS, Machine Learning, Data Analysis, TensorFlow, Agile, API Development"
            ),
            HumanMessage(content=f"Extract keywords from the following Job Description:\n\n{jd_text}")
        ]
    )
    keyword_chain = keyword_extraction_prompt | llm | StrOutputParser()
    keywords_str = keyword_chain.invoke({"jd_text": jd_text})

    keywords = [k.strip() for k in keywords_str.split(',') if k.strip()]
    return list(set(keywords))


def calculate_ats_score(resume_content, jd_text, jd_keywords):
    """Uses LLM to calculate an ATS-like score and provide rationale."""
    ats_score_prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessage(
                "You are an Applicant Tracking System (ATS) evaluator. Your task is to assess how well "
                "a given resume matches a job description, focusing on skills, experience, and requirements. "
                "Provide a match score out of 100 and a brief explanation of the score, highlighting "
                "strengths and areas for improvement. Be concise."
            ),
            HumanMessage(content=f"""
Job Description:
{jd_text}

Candidate Resume:
{resume_content}

Extracted Job Description Keywords: {', '.join(jd_keywords)}

Provide an ATS score (out of 100) and a concise rationale.
Format:
Score: XX/100
Rationale: [Your explanation here]
""")
        ]
    )
    ats_chain = ats_score_prompt | llm | StrOutputParser()
    response = ats_chain.invoke({"resume_content": resume_content, "jd_text": jd_text, "jd_keywords": jd_keywords})

    score_match = re.search(r"Score:\s*(\d+)/100", response)
    rationale_match = re.search(r"Rationale:\s*(.*)", response, re.DOTALL)

    score = int(score_match.group(1)) if score_match else "N/A"
    rationale = rationale_match.group(1).strip() if rationale_match else "Could not extract rationale."

    return score, rationale


def get_missing_keywords(resume_content, jd_keywords):
    """Identifies JD keywords missing from the resume."""
    missing = []
    resume_lower = resume_content.lower()
    for keyword in jd_keywords:
        if keyword.lower() not in resume_lower:
            missing.append(keyword)
    return missing


# --- ANSWER ANALYSIS & FEEDBACK FUNCTIONS ---

def analyze_and_feedback_answer(question, answer, jd_text, resume_content, chat_history_str):
    """
    Analyzes the candidate's answer and provides feedback, and suggests next action.
    Returns feedback and a suggested next_action_type ('continue', 'pivot_behavioral', 'pivot_foundational', 'clarify', 'end_interview').
    """
    analysis_prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessage(
                "You are an expert interview coach and an AI language model. "
                "Your task is to analyze a candidate's answer to an interview question "
                "in the context of the job description and their resume. "
                "Provide constructive feedback. Also, determine the appropriate 'next_action_type' "
                "for the interviewer based on the answer's content and its implications."
                "\n\n**Feedback Criteria:**"
                "\n- **Relevance:** Was the answer relevant to the question and the job role?"
                "\n- **Clarity & Conciseness:** Was it easy to understand and to the point?"
                "\n- **Completeness:** Did it fully address the question? (e.g., used STAR method for behavioral questions?)"
                "\n- **Accuracy:** Was the information presented accurate and consistent with their resume?"
                "\n- **Adaptability:** If the candidate explicitly denied knowledge or implied dishonesty, acknowledge this."
                "\n\n**Next Action Types (choose one):**"
                "\n- `CONTINUE`: The answer was generally good, proceed with a normal follow-up question related to the JD/Resume."
                "\n- `PIVOT_BEHAVIORAL`: The candidate denied knowledge of a technical skill, needs a behavioral question (e.g., problem-solving, learning new things)."
                "\n- `PIVOT_FOUNDATIONAL`: The candidate denied knowledge of a technical skill, needs a more basic/foundational technical question."
                "\n- `CLARIFY`: The answer was vague, unclear, or contradictory, needs a clarifying question."
                "\n- `END_INTERVIEW`: The candidate's answer was highly inappropriate, dismissive, or clearly indicates they are not a fit (e.g., admitting resume is fake, refusal to answer)."
                "\n\nFormat your response strictly as follows:"
                "\nFEEDBACK: [Your constructive feedback here]"
                "\nACTION: [CONTINUE|PIVOT_BEHAVIORAL|PIVOT_FOUNDATIONAL|CLARIFY|END_INTERVIEW]"
            ),
            HumanMessage(content=f"""
Job Description:
{jd_text}

Resume Context:
{resume_content}

Interview History (for context of previous exchanges):
{chat_history_str}

Last Question: {question}
Candidate's Answer: {answer}
""")
        ]
    )
    analysis_chain = analysis_prompt | llm | StrOutputParser()
    response_str = analysis_chain.invoke({
        "question": question,
        "answer": answer,
        "jd_text": jd_text,
        "resume_content": resume_content,
        "chat_history_str": chat_history_str
    })

    feedback_match = re.search(r"FEEDBACK:\s*(.*)", response_str, re.DOTALL)
    action_match = re.search(r"ACTION:\s*([A-Z_]+)", response_str)

    feedback = feedback_match.group(1).strip() if feedback_match else "No feedback generated."
    action = action_match.group(1).strip() if action_match else "CONTINUE"  # Default to continue

    return feedback, action


# --- NEW: PROMPT TEMPLATES FOR DIFFERENT STAGES ---

# Initial/Warm-up Question
INITIAL_WARMUP_PROMPT_TEMPLATE = """
You are an AI mock interviewer for a {job_role} position.
Your goal is to start the interview with a welcoming and relevant opening question.

--- Job Description ---
{jd_context}

--- Candidate's Resume ---
{resume_context}

Based on these documents, generate the **first** interview question for the candidate.
This question should be a general opening, like "Tell me about yourself" or "Walk me through your resume," framed to be relevant to the {job_role} as described in the JD.
Do NOT answer the question yourself. Just provide the question.
Ensure the question is a clear, single question.
"""

# Foundational Language/DSA/Problem Solving Question
FOUNDATIONAL_QUESTION_PROMPT_TEMPLATE = """
You are an AI mock interviewer for a {job_role} position.
Your current focus is to assess the candidate's foundational programming skills, data structures, algorithms, or basic problem-solving abilities.
You should ask questions that are language-agnostic where possible, or if a language is specified in the JD/Resume, prefer that one.
Avoid direct questions from the resume or JD for now.

--- Job Description (for general context of role) ---
{jd_context}

--- Candidate's Resume (for general context of their background) ---
{resume_context}

--- Interview History (for context) ---
{chat_history}

Generate a concise technical interview question focused on one of these areas:
- Core programming language concepts (e.g., Python basics, object-oriented principles, common built-in functions)
- Data Structures (e.g., Arrays, Linked Lists, Trees, Hash Maps)
- Algorithms (e.g., Sorting, Searching, Recursion)
- Basic Problem Solving / Logic

Example: "Explain the difference between a list and a tuple in Python." or "How would you find the middle element of a singly linked list?"
Do NOT answer the question yourself. Just provide the question.
Ensure the question is a clear, single question.
"""

# JD/Resume Specific Question (adapted from previous subsequent_question_prompt_template)
JD_RESUME_SPECIFIC_PROMPT_TEMPLATE = """
You are an AI mock interviewer for a {job_role} position.
Your goal is to assess the candidate's fit for the {job_role} role based on their resume and the job description, focusing on their specific experience and projects.
You have just asked the previous question and received the candidate's answer.

--- Job Description ---
{jd_context}

--- Candidate's Resume ---
{resume_content}

--- Retrieved Context ---
Below is additional context retrieved from the documents, highly relevant to our discussion or the current topic:
{retrieved_context}

--- Current Interview History ---
{chat_history}

Based on all the above, including the candidate's **MOST RECENT ANSWER**, generate the **next logical interview question**.

**IMPORTANT INSTRUCTIONS FOR ADAPTIVE QUESTIONING:**
1.  **Acknowledge and Adapt:**
    * If the candidate explicitly states they don't know a topic, haven't used a specific technology, or express a lack of experience in an area you just asked about, **acknowledge their answer**.
    * Then, **pivot** the question:
        * Ask about a foundational concept related to that area.
        * Ask about a different but related skill from the JD/Resume.
        * Ask a behavioral question about how they would approach learning new technologies, problem-solving, or handling unfamiliar situations.
        * Do NOT keep asking about a specific skill they have just explicitly denied knowledge of.
2.  **Clarification:** If the candidate's answer is vague, unclear, or contradictory, ask a clarifying follow-up question.
3.  **Professionalism:** Maintain a professional and polite tone.
4.  **Focus:** The question should still aim to assess their capabilities relevant to the {job_role}.
5.  **Format:** Do NOT answer the question yourself. Just provide a clear, single question.
"""


# --- Flask Routes ---

@app.route('/')
def index():
    llm_test_response = "LLM Test Not Run Yet."
    try:
        test_prompt = "Hello, tell me something interesting about Python in one sentence."
        response = llm.invoke(test_prompt)
        llm_test_response = f"LLM Test Successful! Response: {response.content[:70]}..."
        print(llm_test_response)
    except Exception as e:
        llm_test_response = f"LLM Test Failed: {e}"
        print(f"LLM Test Failed: {e}")

    return render_template('index.html', llm_test_response=llm_test_response)


@app.route('/upload_documents', methods=['GET', 'POST'])
def upload_documents():
    global db, retriever, global_jd_text, global_resume_content

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
            resume_filepath = os.path.join(app.config['UPLOAD_FOLDER'], resume_filename)
            resume_file.save(resume_filepath)
            resume_chunks = load_and_split_file_document(resume_filepath)
            global_resume_content = "\n".join([c.page_content for c in resume_chunks])

            # --- Process JD Text ---
            global_jd_text = jd_text
            jd_chunks = process_text_to_chunks(jd_text)

            all_chunks = resume_chunks + jd_chunks

            print("\n--- Combined Chunks (First 3) ---")
            for i, chunk in enumerate(all_chunks[:3]):
                print(f"Chunk {i + 1}:\n{chunk.page_content[:200]}...\n")

            # --- ChromaDB Processing ---
            if os.path.exists(CHROMA_DB_DIR) and os.listdir(CHROMA_DB_DIR):
                shutil.rmtree(CHROMA_DB_DIR)
            os.makedirs(CHROMA_DB_DIR, exist_ok=True)

            print(f"Creating ChromaDB from {len(all_chunks)} chunks...")
            db = Chroma.from_documents(
                documents=all_chunks,
                embedding=embeddings,
                persist_directory=CHROMA_DB_DIR
            )
            db.persist()
            print("ChromaDB created and persisted successfully!")

            # --- ATS Score & Missing Keywords Calculation ---
            print("\n--- Calculating ATS Score and Keywords ---")
            jd_keywords = get_jd_keywords(global_jd_text)
            ats_score, ats_rationale = calculate_ats_score(global_resume_content, global_jd_text, jd_keywords)
            missing_keywords = get_missing_keywords(global_resume_content, jd_keywords)

            session['ats_results'] = {
                'score': ats_score,
                'rationale': ats_rationale,
                'jd_keywords': jd_keywords,
                'missing_keywords': missing_keywords
            }
            print(f"ATS Score: {ats_score}/100")
            print(f"Missing Keywords: {missing_keywords}")

            # --- Initialize Retriever and Interview State ---
            retriever = db.as_retriever(search_kwargs={"k": 3})

            # Initialize interview stage and question count
            session['current_stage'] = 'FOUNDATIONAL_WARMUP'  # Start with warm-up
            session['stage_question_count'] = 0
            session['max_foundational_questions'] = 3  # Example: ask up to 3 foundational/warmup questions

            # Generate the very first question based on the initial warm-up prompt
            initial_question_generation_prompt = ChatPromptTemplate.from_template(INITIAL_WARMUP_PROMPT_TEMPLATE)
            initial_question_generator_chain = (
                    initial_question_generation_prompt
                    | llm
                    | StrOutputParser()
            )

            initial_question_input = {
                "job_role": "Software Engineer",  # Placeholder, improve this later
                "jd_context": global_jd_text,
                "resume_context": global_resume_content  # Corrected variable name
            }
            initial_question = initial_question_generator_chain.invoke(initial_question_input)

            interview_history = [{"question": initial_question, "answer": None, "feedback": None}]
            session['interview_history'] = interview_history

            flash('Documents uploaded, processed, and analyzed successfully! Review your ATS score and keywords below.',
                  'success')
            return redirect(url_for('upload_documents'))  # Redirect back to show ATS results

        except Exception as e:
            flash(f'Error processing files: {e}', 'danger')
            print(f"Error during file processing: {e}")
            return redirect(request.url)

    ats_results = session.get('ats_results')
    return render_template('upload_documents.html', ats_results=ats_results)


@app.route('/start_interview')
def start_interview():
    current_interview_history = session.get('interview_history', [])

    global db
    if db is None or not current_interview_history:
        flash("Please upload documents first to start the interview.", "warning")
        return redirect(url_for('upload_documents'))

    current_question = current_interview_history[-1]["question"]
    # Pass current stage for potential UI indication (optional)
    current_stage = session.get('current_stage', 'Unknown')

    return render_template('interview.html', question=current_question, interview_history=current_interview_history,
                           current_stage=current_stage)


@app.route('/interview_flow', methods=['POST'])
def interview_flow():
    global db, llm, retriever, global_jd_text, global_resume_content

    interview_history = session.get('interview_history', [])
    if not interview_history:
        flash("Interview session lost. Please upload documents again.", "danger")
        return redirect(url_for('upload_documents'))

    if db is None or retriever is None:  # question_generator_chain is now dynamic
        flash("Interview setup incomplete. Please upload documents.", "danger")
        return redirect(url_for('upload_documents'))

    user_answer = request.form.get('user_answer')
    if not user_answer:
        flash("Please provide an answer to continue.", "warning")
        return render_template('interview.html', question=interview_history[-1]["question"],
                               interview_history=interview_history)

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
    feedback, next_action_type = analyze_and_feedback_answer(
        last_question,
        user_answer,
        global_jd_text,
        global_resume_content,
        formatted_chat_history
    )

    interview_history[-1]["feedback"] = feedback
    session['interview_history'] = interview_history

    print(f"\n--- Answer Analysis ---\nFeedback: {feedback}\nNext Action: {next_action_type}")

    # --- Conditional Logic for Next Question/Action & Stage Management ---
    current_stage = session.get('current_stage', 'FOUNDATIONAL_WARMUP')
    stage_question_count = session.get('stage_question_count', 0)

    # If the answer was problematic, override normal stage progression
    if next_action_type == "END_INTERVIEW":
        flash(f"Interview Concluded: {feedback}", "info")
        return redirect(url_for('end_interview'))
    elif next_action_type in ["PIVOT_BEHAVIORAL", "PIVOT_FOUNDATIONAL", "CLARIFY"]:
        # Don't increment stage_question_count if pivoting/clarifying
        # These actions aim to resolve issues within the current stage or handle denial
        pass  # Will use specific prompts below
    else:  # next_action_type == "CONTINUE"
        stage_question_count += 1
        session['stage_question_count'] = stage_question_count

    # Determine next stage if applicable
    if current_stage == 'FOUNDATIONAL_WARMUP' and stage_question_count >= session['max_foundational_questions']:
        # Transition to JD/Resume Specific questions
        session['current_stage'] = 'JD_RESUME_SPECIFIC'
        session['stage_question_count'] = 0  # Reset count for new stage
        print(f"--- Transitioning to stage: {session['current_stage']} ---")

    # Prepare common inputs for next question generation
    common_next_question_input = {
        "job_role": "Software Engineer",
        "jd_context": global_jd_text,
        "resume_content": global_resume_content,
        "chat_history": formatted_chat_history
    }

    next_question_prompt_template = ""
    retrieved_context = ""  # Only populate if JD_RESUME_SPECIFIC stage

    # --- Select Prompt Template based on Action Type and Current Stage ---
    if next_action_type == "CLARIFY":
        next_question_prompt_template = CLARIFYING_PROMPT_TEMPLATE  # Needs to be defined
    elif next_action_type == "PIVOT_BEHAVIORAL":
        next_question_prompt_template = PIVOT_BEHAVIORAL_PROMPT_TEMPLATE  # Needs to be defined
    elif next_action_type == "PIVOT_FOUNDATIONAL":
        next_question_prompt_template = PIVOT_FOUNDATIONAL_PROMPT_TEMPLATE  # Needs to be defined
    elif session['current_stage'] == 'FOUNDATIONAL_WARMUP':
        next_question_prompt_template = FOUNDATIONAL_QUESTION_PROMPT_TEMPLATE
    elif session['current_stage'] == 'JD_RESUME_SPECIFIC':
        # For JD_RESUME_SPECIFIC, we need retrieved context
        query_for_retriever = f"Generate a follow-up question based on the candidate's answer. Previous Question: {last_question}\nCandidate's Answer: {user_answer}"
        retrieved_docs = retriever.invoke(query_for_retriever)
        retrieved_context = "\n".join([d.page_content for d in retrieved_docs])
        common_next_question_input["retrieved_context"] = retrieved_context  # Add to input
        next_question_prompt_template = JD_RESUME_SPECIFIC_PROMPT_TEMPLATE
    else:
        # Fallback or error case
        flash("Unexpected interview stage or action type. Ending interview.", "danger")
        return redirect(url_for('end_interview'))

    # Define the specific prompt templates that are used by the analyze_and_feedback_answer function
    # These were previously embedded directly in interview_flow, now extracted for clarity and reuse
    CLARIFYING_PROMPT_TEMPLATE = """
    You are an AI mock interviewer for a {job_role} position. The candidate's last answer was unclear or vague.
    Your goal is to ask a clarifying follow-up question to better understand their previous response.

    --- Job Description ---
    {jd_context}

    --- Candidate's Resume ---
    {resume_content}

    --- Retrieved Context ---
    Relevant information from documents:
    {retrieved_context}

    --- Current Interview History ---
    {chat_history}

    Based on the last question and the candidate's unclear answer, ask a concise clarifying question.
    Do NOT ask a new topic question. Just seek clarification.
    """

    PIVOT_BEHAVIORAL_PROMPT_TEMPLATE = """
    You are an AI mock interviewer for a {job_role} position. The candidate has indicated a lack of experience or knowledge regarding a recent technical question.
    Your goal is to pivot the interview to a **behavioral question** that still assesses their capabilities for the role, such as problem-solving, learning agility, teamwork, or handling challenges.

    --- Job Description ---
    {jd_context}

    --- Candidate's Resume ---
    {resume_content}

    --- Relevant Context (for inspiration, not direct questioning) ---
    {retrieved_context}

    --- Current Interview History ---
    {chat_history}

    Acknowledging their previous answer (e.g., about not knowing a specific tech), ask a relevant behavioral question for the {job_role} position.
    Example: "Given you mentioned not having direct experience with X, how do you typically approach learning a new technology or tackling a problem you're unfamiliar with?"
    Do NOT ask another technical question about topics they denied.
    """

    PIVOT_FOUNDATIONAL_PROMPT_TEMPLATE = """
    You are an AI mock interviewer for a {job_role} position. The candidate has indicated a lack of experience or knowledge regarding a recent technical question about a specific technology or advanced concept.
    Your goal is to pivot the interview to a **more foundational or conceptual technical question** related to the area, rather than a specific tool or advanced application. Assess their understanding of underlying principles.

    --- Job Description ---
    {jd_context}

    --- Candidate's Resume ---
    {resume_content}

    --- Relevant Context (for inspiration, not direct questioning) ---
    {retrieved_context}

    --- Current Interview History ---
    {chat_history}

    Acknowledging their previous answer (e.g., about not knowing a specific tech), ask a more foundational or conceptual technical question for the {job_role} position.
    Example: "While you may not have direct experience with X, can you explain the core concepts of Y (which is related to X)?"
    Do NOT ask another question about the specific technology they denied.
    """

    # Generate the next question using the selected prompt template
    question_generator_chain_for_stage = ChatPromptTemplate.from_template(
        next_question_prompt_template) | llm | StrOutputParser()
    next_question = question_generator_chain_for_stage.invoke(common_next_question_input)

    # Add the new question to history
    interview_history.append({"question": next_question, "answer": None, "feedback": None})
    session['interview_history'] = interview_history

    return redirect(url_for('start_interview'))


@app.route('/end_interview')
def end_interview():
    """Clears the interview session and redirects to the upload page."""
    session.pop('interview_history', None)
    session.pop('ats_results', None)
    session.pop('current_stage', None)
    session.pop('stage_question_count', None)
    session.pop('max_foundational_questions', None)

    global db, retriever, global_jd_text, global_resume_content  # question_generator_chain is no longer global
    db = None
    retriever = None
    global_jd_text = ""
    global_resume_content = ""

    if os.path.exists(CHROMA_DB_DIR):
        shutil.rmtree(CHROMA_DB_DIR)
        os.makedirs(CHROMA_DB_DIR, exist_ok=True)

    flash("Interview ended. Please upload new documents to start a new session.", "info")
    return redirect(url_for('upload_documents'))


if __name__ == '__main__':
    app.run(debug=True)
