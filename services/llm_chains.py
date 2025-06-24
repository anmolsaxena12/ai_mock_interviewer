from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, SystemMessage
import re

# Initialize LLM (passed from app context or imported after config)
llm = None # This will be set from app.py after Flask app creation

def set_llm_instance(llm_instance):
    global llm
    llm = llm_instance

# --- Prompt Templates ---

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

# --- LLM Chain Definitions ---

def get_initial_question_chain():
    return ChatPromptTemplate.from_template(INITIAL_WARMUP_PROMPT_TEMPLATE) | llm | StrOutputParser()

def get_foundational_question_chain():
    return ChatPromptTemplate.from_template(FOUNDATIONAL_QUESTION_PROMPT_TEMPLATE) | llm | StrOutputParser()

def get_jd_resume_specific_chain():
    return ChatPromptTemplate.from_template(JD_RESUME_SPECIFIC_PROMPT_TEMPLATE) | llm | StrOutputParser()

def get_clarifying_question_chain():
    return ChatPromptTemplate.from_template(CLARIFYING_PROMPT_TEMPLATE) | llm | StrOutputParser()

def get_pivot_behavioral_chain():
    return ChatPromptTemplate.from_template(PIVOT_BEHAVIORAL_PROMPT_TEMPLATE) | llm | StrOutputParser()

def get_pivot_foundational_chain():
    return ChatPromptTemplate.from_template(PIVOT_FOUNDATIONAL_PROMPT_TEMPLATE) | llm | StrOutputParser()

def get_ats_score_chain():
    return ChatPromptTemplate.from_messages(
        [
            SystemMessage(
                "You are an Applicant Tracking System (ATS) evaluator. Your task is to assess how well "
                "a given resume matches a job description, focusing on skills, experience, and requirements. "
                "Provide a match score out of 100 and a brief explanation of the score, highlighting "
                "strengths and areas for improvement. Be concise."
            ),
            HumanMessage(content="""
Job Description:
{jd_text}

Candidate Resume:
{resume_content}

Extracted Job Description Keywords: {jd_keywords_str}

Provide an ATS score (out of 100) and a concise rationale.
Format:
Score: XX/100
Rationale: [Your explanation here]
""")
        ]
    ) | llm | StrOutputParser()

def get_keyword_extraction_chain():
    return ChatPromptTemplate.from_messages(
        [
            SystemMessage(
                "You are an expert HR assistant. Your task is to identify and list "
                "the most important technical skills, tools, programming languages, methodologies, "
                "and core requirements mentioned in the job description. "
                "List them as a comma-separated string, prioritize single words or short phrases. "
                "Exclude common words like 'experience', 'ability', 'strong', 'good communication', 'team player', 'responsible', 'collaborate'. "
                "Example: Python, SQL, AWS, Machine Learning, Data Analysis, TensorFlow, Agile, API Development"
            ),
            HumanMessage(content="Extract keywords from the following Job Description:\n\n{jd_text}")
        ]
    ) | llm | StrOutputParser()


def get_answer_analysis_chain():
    return ChatPromptTemplate.from_messages(
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
            HumanMessage(content="""
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
    ) | llm | StrOutputParser()