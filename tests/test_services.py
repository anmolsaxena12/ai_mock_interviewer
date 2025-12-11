"""
Unit tests for service layer components.

Tests for document processing, ATS analysis, interview management, and LLM chains.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from langchain.schema import Document


class TestDocumentProcessor:
    """Tests for document_processor service"""
    
    def test_process_text_to_chunks(self):
        """Test text splitting into chunks"""
        from services import document_processor
        
        text = "This is a test document. " * 100  # Long text
        chunks = document_processor.process_text_to_chunks(text, source="Test")
        
        assert len(chunks) > 0
        assert all(isinstance(chunk, Document) for chunk in chunks)
        assert all(chunk.metadata['source'] == 'Test' for chunk in chunks)
    
    def test_process_empty_text(self):
        """Test processing empty text"""
        from services import document_processor
        
        chunks = document_processor.process_text_to_chunks("")
        assert chunks == []
        
        chunks = document_processor.process_text_to_chunks("   ")
        assert chunks == []
    
    @patch('services.document_processor.PyPDFLoader')
    def test_load_pdf_document(self, mock_pdf_loader):
        """Test loading PDF document"""
        from services import document_processor
        
        # Mock PDF loader
        mock_loader_instance = MagicMock()
        mock_loader_instance.load.return_value = [
            Document(page_content="PDF content here", metadata={'source': 'test.pdf'})
        ]
        mock_pdf_loader.return_value = mock_loader_instance
        
        chunks = document_processor.load_and_split_file_document('test.pdf')
        
        assert len(chunks) > 0
        mock_pdf_loader.assert_called_once_with('test.pdf')
    
    @patch('services.document_processor.Docx2txtLoader')
    def test_load_docx_document(self, mock_docx_loader):
        """Test loading DOCX document"""
        from services import document_processor
        
        # Mock DOCX loader
        mock_loader_instance = MagicMock()
        mock_loader_instance.load.return_value = [
            Document(page_content="DOCX content here", metadata={'source': 'test.docx'})
        ]
        mock_docx_loader.return_value = mock_loader_instance
        
        chunks = document_processor.load_and_split_file_document('test.docx')
        
        assert len(chunks) > 0
        mock_docx_loader.assert_called_once_with('test.docx')
    
    def test_load_unsupported_file(self):
        """Test loading unsupported file type"""
        from services import document_processor
        
        with pytest.raises(ValueError, match="Unsupported file type"):
            document_processor.load_and_split_file_document('test.txt')
    
    @patch('services.document_processor.Chroma')
    @patch('services.document_processor.get_embeddings_model')
    def test_initialize_vector_db(self, mock_embeddings, mock_chroma, mock_document_chunks, tmp_path):
        """Test vector database initialization"""
        from services import document_processor
        
        # Mock embeddings
        mock_embeddings.return_value = MagicMock()
        
        # Mock Chroma
        mock_db = MagicMock()
        mock_chroma.from_documents.return_value = mock_db
        
        chroma_dir = str(tmp_path / "test_chroma")
        document_processor.initialize_vector_db(mock_document_chunks, chroma_dir)
        
        # Verify database was created and persisted
        mock_chroma.from_documents.assert_called_once()
        mock_db.persist.assert_called_once()
    
    def test_get_retriever(self):
        """Test retriever creation"""
        from services import document_processor
        
        # Test with no DB
        document_processor._db = None
        retriever = document_processor.get_retriever()
        assert retriever is None
        
        # Test with DB
        mock_db = MagicMock()
        document_processor.set_vector_store(mock_db)
        retriever = document_processor.get_retriever()
        
        assert retriever is not None
        mock_db.as_retriever.assert_called_once()


class TestATSAnalyzer:
    """Tests for ATS analyzer service"""
    
    @patch('services.llm_chains.get_keyword_extraction_chain')
    def test_get_jd_keywords(self, mock_chain_getter):
        """Test keyword extraction from job description"""
        from services import ats_analyzer
        
        # Mock the chain
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = "Python, Flask, REST API, SQL, Machine Learning"
        mock_chain_getter.return_value = mock_chain
        
        jd_text = "Looking for a Python developer with Flask and REST API experience"
        keywords = ats_analyzer.get_jd_keywords(jd_text)
        
        assert isinstance(keywords, list)
        assert len(keywords) > 0
        assert 'Python' in keywords
        assert 'Flask' in keywords
    
    @patch('services.llm_chains.get_ats_score_chain')
    def test_calculate_ats_score(self, mock_chain_getter):
        """Test ATS score calculation"""
        from services import ats_analyzer
        
        # Mock the chain
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = "Score: 85/100\nRationale: Strong match with required skills."
        mock_chain_getter.return_value = mock_chain
        
        resume = "Python developer with Flask experience"
        jd = "Looking for Python developer"
        keywords = ['Python', 'Flask']
        
        score, rationale = ats_analyzer.calculate_ats_score(resume, jd, keywords)
        
        assert score == 85
        assert "Strong match" in rationale
    
    @patch('services.llm_chains.get_ats_score_chain')
    def test_calculate_ats_score_invalid_response(self, mock_chain_getter):
        """Test ATS score with invalid LLM response"""
        from services import ats_analyzer
        
        # Mock chain with invalid response
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = "Invalid response format"
        mock_chain_getter.return_value = mock_chain
        
        score, rationale = ats_analyzer.calculate_ats_score("resume", "jd", ['Python'])
        
        assert score == "N/A"
        assert "Could not extract rationale" in rationale
    
    def test_get_missing_keywords(self):
        """Test finding missing keywords in resume"""
        from services import ats_analyzer
        
        resume = "Python developer with Flask and SQL experience"
        keywords = ['Python', 'Flask', 'Docker', 'Kubernetes', 'SQL']
        
        missing = ats_analyzer.get_missing_keywords(resume, keywords)
        
        assert 'Docker' in missing
        assert 'Kubernetes' in missing
        assert 'Python' not in missing
        assert 'Flask' not in missing
    
    def test_get_missing_keywords_case_insensitive(self):
        """Test missing keywords with case insensitivity"""
        from services import ats_analyzer
        
        resume = "PYTHON developer with flask"
        keywords = ['Python', 'Flask', 'Docker']
        
        missing = ats_analyzer.get_missing_keywords(resume, keywords)
        
        assert 'Docker' in missing
        assert 'Python' not in missing
        assert 'Flask' not in missing


class TestInterviewManager:
    """Tests for interview manager service"""
    
    @patch('services.llm_chains.get_answer_analysis_chain')
    def test_analyze_and_feedback_answer_continue(self, mock_chain_getter):
        """Test answer analysis with CONTINUE action"""
        from services import interview_manager
        
        # Mock the chain
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = (
            "FEEDBACK: Good answer with relevant details.\n"
            "ACTION: CONTINUE"
        )
        mock_chain_getter.return_value = mock_chain
        
        question = "Tell me about your Python experience"
        answer = "I have 5 years of Python development experience"
        
        feedback, action = interview_manager.analyze_and_feedback_answer(
            question, answer, "JD text", "Resume text", "Chat history"
        )
        
        assert "Good answer" in feedback
        assert action == "CONTINUE"
    
    @patch('services.llm_chains.get_answer_analysis_chain')
    def test_analyze_and_feedback_answer_pivot_behavioral(self, mock_chain_getter):
        """Test answer analysis with PIVOT_BEHAVIORAL action"""
        from services import interview_manager
        
        # Mock the chain
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = (
            "FEEDBACK: Candidate indicated lack of knowledge.\n"
            "ACTION: PIVOT_BEHAVIORAL"
        )
        mock_chain_getter.return_value = mock_chain
        
        question = "Explain Docker containerization"
        answer = "I haven't worked with Docker before"
        
        feedback, action = interview_manager.analyze_and_feedback_answer(
            question, answer, "JD", "Resume", "History"
        )
        
        assert action == "PIVOT_BEHAVIORAL"
    
    @patch('services.llm_chains.get_answer_analysis_chain')
    def test_analyze_and_feedback_answer_end_interview(self, mock_chain_getter):
        """Test answer analysis with END_INTERVIEW action"""
        from services import interview_manager
        
        # Mock the chain
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = (
            "FEEDBACK: Inappropriate response.\n"
            "ACTION: END_INTERVIEW"
        )
        mock_chain_getter.return_value = mock_chain
        
        feedback, action = interview_manager.analyze_and_feedback_answer(
            "Question", "Inappropriate answer", "JD", "Resume", "History"
        )
        
        assert action == "END_INTERVIEW"
    
    @patch('services.interview_manager.session', {'current_stage': 'FOUNDATIONAL_WARMUP', 'stage_question_count': 0})
    def test_update_interview_stage_increment(self):
        """Test interview stage update with count increment"""
        from services import interview_manager
        from flask import session
        
        with patch('services.interview_manager.session', {'current_stage': 'FOUNDATIONAL_WARMUP', 'stage_question_count': 0}):
            interview_manager.update_interview_stage('CONTINUE')
    
    @patch('services.llm_chains.get_foundational_question_chain')
    @patch('services.interview_manager.session')
    def test_get_next_question_foundational(self, mock_session, mock_chain_getter):
        """Test getting next foundational question"""
        from services import interview_manager
        
        # Mock session
        mock_session.get.side_effect = lambda key, default=None: {
            'current_stage': 'FOUNDATIONAL_WARMUP',
            'stage_question_count': 1,
            'interview_history': []
        }.get(key, default)
        
        # Mock chain
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = "What is the difference between a list and tuple?"
        mock_chain_getter.return_value = mock_chain
        
        question, action = interview_manager.get_next_question(
            'CONTINUE', "JD text", "Resume", "History"
        )
        
        assert isinstance(question, str)
        assert len(question) > 0


class TestLLMChains:
    """Tests for LLM chain configurations"""
    
    def test_set_llm_instance(self):
        """Test setting LLM instance"""
        from services import llm_chains
        
        mock_llm = MagicMock()
        llm_chains.set_llm_instance(mock_llm)
        
        assert llm_chains.llm == mock_llm
    
    @patch('services.llm_chains.llm')
    def test_get_initial_question_chain(self, mock_llm):
        """Test initial question chain creation"""
        from services import llm_chains
        
        mock_llm.return_value = "Test question"
        chain = llm_chains.get_initial_question_chain()
        
        assert chain is not None
    
    @patch('services.llm_chains.llm')
    def test_get_foundational_question_chain(self, mock_llm):
        """Test foundational question chain creation"""
        from services import llm_chains
        
        mock_llm.return_value = "Test question"
        chain = llm_chains.get_foundational_question_chain()
        
        assert chain is not None
    
    @patch('services.llm_chains.llm')
    def test_get_ats_score_chain(self, mock_llm):
        """Test ATS score chain creation"""
        from services import llm_chains
        
        mock_llm.return_value = "Score: 85/100\nRationale: Good"
        chain = llm_chains.get_ats_score_chain()
        
        assert chain is not None


class TestConfig:
    """Tests for configuration"""
    
    def test_config_values(self):
        """Test configuration values are set correctly"""
        from config import Config
        
        assert hasattr(Config, 'UPLOAD_FOLDER')
        assert hasattr(Config, 'CHROMA_DB_DIR')
        assert hasattr(Config, 'ALLOWED_EXTENSIONS')
        assert hasattr(Config, 'MAX_FOUNDATIONAL_QUESTIONS')
    
    def test_allowed_extensions(self):
        """Test allowed file extensions"""
        from config import Config
        
        assert 'pdf' in Config.ALLOWED_EXTENSIONS
        assert 'docx' in Config.ALLOWED_EXTENSIONS
        assert 'txt' not in Config.ALLOWED_EXTENSIONS

