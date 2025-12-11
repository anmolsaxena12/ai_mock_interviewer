"""
Mock test data and fixtures for testing.

This file contains sample data used across tests.
"""

SAMPLE_JOB_DESCRIPTION = """
Software Engineer - Python Developer

We are seeking a skilled Python developer to join our team.

Requirements:
- 3+ years of Python development experience
- Experience with Flask or Django web frameworks
- Strong understanding of REST APIs
- Knowledge of SQL databases
- Experience with Machine Learning is a plus
- Excellent problem-solving skills

Responsibilities:
- Develop and maintain web applications
- Design and implement REST APIs
- Collaborate with cross-functional teams
- Write clean, maintainable code
"""

SAMPLE_RESUME = """
John Doe
Software Engineer

EXPERIENCE:
Senior Python Developer at Tech Corp (2020-2023)
- Developed REST APIs using Flask
- Implemented machine learning models for data analysis
- Worked with PostgreSQL databases
- Led a team of 3 developers

Python Developer at StartupXYZ (2018-2020)
- Built web applications using Django
- Developed automated testing frameworks
- Implemented CI/CD pipelines

SKILLS:
- Programming: Python, JavaScript, SQL
- Frameworks: Flask, Django, FastAPI
- Databases: PostgreSQL, MongoDB
- Tools: Docker, Git, Jenkins

EDUCATION:
B.S. Computer Science, University of Technology (2018)
"""

SAMPLE_INTERVIEW_QUESTIONS = [
    "Tell me about yourself and your background in software engineering.",
    "Can you explain your experience with Flask web framework?",
    "Describe a challenging project you worked on and how you solved it.",
    "What is your understanding of REST API design principles?",
    "How do you approach debugging complex issues in production?"
]

SAMPLE_ANSWERS = {
    "good": "I have 5 years of experience working with Python and Flask. I've built multiple REST APIs and have a strong understanding of API design principles.",
    "vague": "I've worked with Python.",
    "deny_knowledge": "I haven't worked with that technology before.",
    "inappropriate": "I don't want to answer this question."
}

ATS_KEYWORDS = [
    "Python", "Flask", "Django", "REST API", "SQL", 
    "Machine Learning", "PostgreSQL", "Docker", "Git"
]


