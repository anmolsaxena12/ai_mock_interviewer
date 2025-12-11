"""
Pytest configuration and fixtures for the AI Mock Interviewer test suite.
This file contains shared fixtures and configuration for all tests.
"""
import os
import sys
import pytest
import tempfile
import shutil
from flask import session
from unittest.mock import Mock, MagicMock, patch

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from config import Config

class TestConfig(Config):
    """Test-specific configuration"""
    TESTING = True
    SECRET_KEY = 'test-secret-key'
    UPLOAD_FOLDER = 'test_uploads'
    CHROMA_DB_DIR = 'test_chroma_db'
    # Mock the Google API key for testing
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "test-google-api-key")
    MAX_FOUNDATIONAL_QUESTIONS = 2  # Reduced for faster tests
    WTF_CSRF_ENABLED = False


@pytest.fixture
def app():
    """Create and configure a test Flask application instance"""
    # Create temp directories for testing
    test_upload_folder = 'test_uploads'
    test_chroma_dir = 'test_chroma_db'
    os.makedirs(test_upload_folder, exist_ok=True)
    os.makedirs(test_chroma_dir, exist_ok=True)
    
    # Import and create app
    from app import create_app
    app = create_app()
    app.config.from_object(TestConfig)
    
    # Set up test context
    app.config['TESTING'] = True
    
    yield app
    
    # Cleanup after tests
    if os.path.exists(test_upload_folder):
        shutil.rmtree(test_upload_folder)
    if os.path.exists(test_chroma_dir):
        shutil.rmtree(test_chroma_dir)


@pytest.fixture
def client(app):
    """Create a test client for the Flask application"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create a CLI runner for testing CLI commands"""
    return app.test_cli_runner()


@pytest.fixture
def mock_llm():
    """Mock LLM responses for testing without API calls"""
    mock = MagicMock()
    
    # Mock invoke method for different response types
    def invoke_side_effect(prompt):
        if isinstance(prompt, str):
            if "keyword" in prompt.lower():
                return Mock(content="Python, Flask, Machine Learning, REST API, SQL")
            elif "score" in prompt.lower():
                return Mock(content="Score: 85/100\nRationale: Good match with strong Python skills.")
            else:
                return Mock(content="Tell me about your experience with Python.")
        elif isinstance(prompt, dict):
            return "Tell me about yourself and your background in software engineering."
        return Mock(content="Default mock response")
    
    mock.invoke.side_effect = invoke_side_effect
    return mock


@pytest.fixture
def sample_jd_text():
    """Sample job description for testing"""
    return """
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


@pytest.fixture
def sample_resume_content():
    """Sample resume content for testing"""
    return """
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


@pytest.fixture
def mock_pdf_file(tmp_path):
    """Create a mock PDF file for testing"""
    pdf_file = tmp_path / "test_resume.pdf"
    # Create a simple text file (in real tests, you'd use PyPDF2 to create actual PDFs)
    pdf_file.write_text("Mock resume content for testing")
    return pdf_file


@pytest.fixture
def mock_vector_db():
    """Mock ChromaDB vector store for testing"""
    mock_db = MagicMock()
    mock_db.as_retriever.return_value = MagicMock()
    mock_db.persist.return_value = None
    return mock_db


@pytest.fixture
def session_with_interview(client):
    """Set up a test session with interview state"""
    with client.session_transaction() as sess:
        sess['interview_history'] = [
            {
                "question": "Tell me about yourself.",
                "answer": "I'm a Python developer with 5 years of experience.",
                "feedback": None
            }
        ]
        sess['current_stage'] = 'FOUNDATIONAL_WARMUP'
        sess['stage_question_count'] = 1
        sess['ats_results'] = {
            'score': 85,
            'rationale': 'Good match',
            'jd_keywords': ['Python', 'Flask', 'REST API'],
            'missing_keywords': ['Docker']
        }
    return client


@pytest.fixture
def mock_document_chunks():
    """Create mock document chunks for testing"""
    from langchain.schema import Document
    return [
        Document(page_content="Python developer with Flask experience", metadata={'source': 'Resume'}),
        Document(page_content="Machine Learning projects using TensorFlow", metadata={'source': 'Resume'}),
        Document(page_content="REST API development and microservices", metadata={'source': 'Job Description'})
    ]


# Autouse fixtures for common setup
@pytest.fixture(autouse=True)
def reset_services():
    """Reset service layer state before each test"""
    from services import document_processor, llm_chains
    document_processor._db = None
    document_processor._embeddings = None
    yield
    # Cleanup after test
    document_processor._db = None
    document_processor._embeddings = None

