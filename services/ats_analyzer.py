import re
from services import llm_chains # Import llm_chains for getting chain functions

def get_jd_keywords(jd_text):
    """Uses LLM to extract key skills and requirements from the Job Description."""
    keyword_chain = llm_chains.get_keyword_extraction_chain()
    keywords_str = keyword_chain.invoke({"jd_text": jd_text})
    
    keywords = [k.strip() for k in keywords_str.split(',') if k.strip()]
    return list(set(keywords))

def calculate_ats_score(resume_content, jd_text, jd_keywords):
    """Uses LLM to calculate an ATS-like score and provide rationale."""
    ats_chain = llm_chains.get_ats_score_chain()
    
    response = ats_chain.invoke({
        "resume_content": resume_content,
        "jd_text": jd_text,
        "jd_keywords_str": ', '.join(jd_keywords) # Pass as string
    })
    
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