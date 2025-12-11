"""
Sample resume PDF content for testing uploads.
This file contains actual resume text that can be converted to PDF for testing.
"""

SAMPLE_RESUME_TEXT = """
JOHN DOE
Senior Python Developer
john.doe@email.com | (555) 123-4567 | LinkedIn: linkedin.com/in/johndoe

PROFESSIONAL SUMMARY
Senior Python Developer with 5+ years of experience building scalable web applications and REST APIs. 
Expertise in Flask, Django, and modern Python frameworks. Strong background in machine learning and data analysis.

TECHNICAL SKILLS
• Programming Languages: Python, JavaScript, SQL, Bash
• Web Frameworks: Flask, Django, FastAPI, React
• Databases: PostgreSQL, MongoDB, Redis, MySQL
• Tools & Technologies: Docker, Kubernetes, Git, Jenkins, AWS
• Machine Learning: TensorFlow, scikit-learn, pandas, NumPy

PROFESSIONAL EXPERIENCE

Senior Python Developer | Tech Corp                                              Jan 2020 - Present
• Developed and maintained 10+ REST APIs using Flask, serving 1M+ requests daily
• Implemented machine learning models for predictive analytics, improving accuracy by 25%
• Led a team of 3 developers in building microservices architecture
• Designed and optimized PostgreSQL databases, reducing query time by 40%
• Implemented CI/CD pipelines using Jenkins and Docker

Python Developer | StartupXYZ                                                    Jun 2018 - Dec 2019
• Built web applications using Django framework for e-commerce platform
• Developed automated testing frameworks achieving 85% code coverage
• Integrated third-party APIs including payment gateways and shipping providers
• Collaborated with frontend team to build RESTful API endpoints
• Participated in agile development process and daily standups

Junior Software Engineer | Innovation Labs                                       Jan 2017 - May 2018
• Developed Python scripts for data processing and automation
• Contributed to open-source projects and maintained documentation
• Assisted in database design and query optimization
• Learned best practices for software development and version control

EDUCATION

Bachelor of Science in Computer Science                                          2016
University of Technology
GPA: 3.8/4.0

CERTIFICATIONS
• AWS Certified Developer - Associate
• Python Programming Certification (Coursera)

PROJECTS

AI Mock Interviewer (Personal Project)
• Built a Flask-based web application for conducting AI-powered mock interviews
• Integrated Google Gemini LLM for intelligent question generation and feedback
• Implemented ATS scoring system using NLP techniques
• Used ChromaDB for document retrieval and semantic search

E-commerce Platform (StartupXYZ)
• Full-stack web application with Django backend and React frontend
• Processed 10,000+ orders with 99.9% uptime
• Integrated Stripe payment processing and real-time inventory management
"""

def create_sample_pdf(output_path):
    """
    Creates a sample PDF file for testing.
    Requires: pip install reportlab
    """
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        
        c = canvas.Canvas(output_path, pagesize=letter)
        width, height = letter
        
        # Add resume text to PDF
        y = height - 50
        for line in SAMPLE_RESUME_TEXT.split('\n'):
            if y < 50:
                c.showPage()
                y = height - 50
            c.drawString(50, y, line[:100])  # Limit line length
            y -= 15
        
        c.save()
        print(f"Sample PDF created at: {output_path}")
        return True
    except ImportError:
        print("reportlab not installed. Install with: pip install reportlab")
        return False


if __name__ == "__main__":
    import os
    fixtures_dir = os.path.join(os.path.dirname(__file__), "..", "test", "fixtures")
    os.makedirs(fixtures_dir, exist_ok=True)
    
    pdf_path = os.path.join(fixtures_dir, "sample_resume.pdf")
    create_sample_pdf(pdf_path)


