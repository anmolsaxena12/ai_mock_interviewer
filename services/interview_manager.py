import re
from flask import session
from services import llm_chains # Import llm_chains for getting chain functions
from services import document_processor # For retriever
from config import Config

def analyze_and_feedback_answer(question, answer, jd_text, resume_content, chat_history_str):
    """
    Analyzes the candidate's answer and provides feedback, and suggests next action.
    Returns feedback and a suggested next_action_type ('continue', 'pivot_behavioral', 'pivot_foundational', 'clarify', 'end_interview').
    """
    analysis_chain = llm_chains.get_answer_analysis_chain()
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
    action = action_match.group(1).strip() if action_match else "CONTINUE" # Default to continue

    return feedback, action

def get_next_question(next_action_type, global_jd_text, global_resume_content, formatted_chat_history):
    """Determines the next question based on interview state and action type."""
    current_stage = session.get('current_stage', 'FOUNDATIONAL_WARMUP')
    stage_question_count = session.get('stage_question_count', 0)

    # Prepare common inputs for next question generation
    common_next_question_input = {
        "job_role": Config.JOB_ROLE,
        "jd_context": global_jd_text,
        "resume_content": global_resume_content,
        "chat_history": formatted_chat_history
    }
    
    next_question_prompt_template_chain = None
    retrieved_context = ""

    # --- Select Prompt Template based on Action Type and Current Stage ---
    if next_action_type == "CLARIFY":
        next_question_prompt_template_chain = llm_chains.get_clarifying_question_chain()
        # Still attempt to get context, it might help clarify relevant details
        query_for_retriever = f"Clarify previous answer: {session['interview_history'][-1]['question']}\nCandidate's Answer: {session['interview_history'][-1]['answer']}"
        retriever_instance = document_processor.get_retriever()
        if retriever_instance:
            retrieved_docs = retriever_instance.invoke(query_for_retriever)
            retrieved_context = "\n".join([d.page_content for d in retrieved_docs])
            common_next_question_input["retrieved_context"] = retrieved_context

    elif next_action_type == "PIVOT_BEHAVIORAL":
        next_question_prompt_template_chain = llm_chains.get_pivot_behavioral_chain()
        # Get general context, not specific to a denied tech
        query_for_retriever = f"General context for behavioral question in {Config.JOB_ROLE} role related to previous denial: {session['interview_history'][-1]['question']}\nCandidate's Answer: {session['interview_history'][-1]['answer']}"
        retriever_instance = document_processor.get_retriever()
        if retriever_instance:
            retrieved_docs = retriever_instance.invoke(query_for_retriever)
            retrieved_context = "\n".join([d.page_content for d in retrieved_docs])
            common_next_question_input["retrieved_context"] = retrieved_context

    elif next_action_type == "PIVOT_FOUNDATIONAL":
        next_question_prompt_template_chain = llm_chains.get_pivot_foundational_chain()
        # Get general context for foundational questions
        query_for_retriever = f"General context for foundational technical question in {Config.JOB_ROLE} role related to previous denial: {session['interview_history'][-1]['question']}\nCandidate's Answer: {session['interview_history'][-1]['answer']}"
        retriever_instance = document_processor.get_retriever()
        if retriever_instance:
            retrieved_docs = retriever_instance.invoke(query_for_retriever)
            retrieved_context = "\n".join([d.page_content for d in retrieved_docs])
            common_next_question_input["retrieved_context"] = retrieved_context

    elif current_stage == 'FOUNDATIONAL_WARMUP':
        next_question_prompt_template_chain = llm_chains.get_foundational_question_chain()
        # No specific retrieval needed for foundational questions initially
        common_next_question_input["retrieved_context"] = "" # Ensure this variable exists for the prompt

    elif current_stage == 'JD_RESUME_SPECIFIC':
        # For JD_RESUME_SPECIFIC, we need retrieved context
        query_for_retriever = f"Generate a follow-up question based on the candidate's answer. Previous Question: {session['interview_history'][-1]['question']}\nCandidate's Answer: {session['interview_history'][-1]['answer']}"
        retriever_instance = document_processor.get_retriever()
        if retriever_instance:
            retrieved_docs = retriever_instance.invoke(query_for_retriever)
            retrieved_context = "\n".join([d.page_content for d in retrieved_docs])
            common_next_question_input["retrieved_context"] = retrieved_context
        next_question_prompt_template_chain = llm_chains.get_jd_resume_specific_chain()
    
    else:
        # Fallback or error case if stage is not recognized
        print(f"Error: Unknown current_stage: {current_stage}")
        return "An internal error occurred. Please restart the interview.", "END_INTERVIEW"

    if next_question_prompt_template_chain is None:
        print(f"Error: No question chain selected for next_action_type: {next_action_type} and stage: {current_stage}")
        return "An internal error occurred. Please restart the interview.", "END_INTERVIEW"

    next_question = next_question_prompt_template_chain.invoke(common_next_question_input)
    return next_question, next_action_type # Return next_action_type just in case, though it's already determined by analyze_and_feedback_answer


def update_interview_stage(next_action_type):
    """Updates the interview stage and question count based on action type."""
    current_stage = session.get('current_stage', 'FOUNDATIONAL_WARMUP')
    stage_question_count = session.get('stage_question_count', 0)

    # Don't increment count for clarifying or pivoting questions, they are follow-ups
    if next_action_type not in ["PIVOT_BEHAVIORAL", "PIVOT_FOUNDATIONAL", "CLARIFY"]:
        stage_question_count += 1
        session['stage_question_count'] = stage_question_count

    # Transition logic
    if current_stage == 'FOUNDATIONAL_WARMUP' and stage_question_count >= Config.MAX_FOUNDATIONAL_QUESTIONS:
        session['current_stage'] = 'JD_RESUME_SPECIFIC'
        session['stage_question_count'] = 0 # Reset count for new stage
        print(f"--- Transitioning to stage: {session['current_stage']} ---")
    
    # Add more stage transitions here if needed (e.g., JD_RESUME_SPECIFIC to BEHAVIORAL)
    
    return session['current_stage']