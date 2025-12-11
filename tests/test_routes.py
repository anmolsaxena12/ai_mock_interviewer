"""
Integration tests for the AI Mock Interviewer application routes.

These tests verify the end-to-end functionality of the Flask application,
including document upload, ATS scoring, and interview flow.
"""
import pytest
import os
import io
from unittest.mock import patch, MagicMock, Mock
from flask import session


class TestIndexRoute:
    """Tests for the home/index route"""
    
    def test_index_page_loads(self, client):
        """Test that the index page loads successfully"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Welcome to the AI Mock Interviewer' in response.data or b'AI Mock Interviewer' in response.data
    
    @patch('routes.ChatGoogleGenerativeAI')
    def test_index_llm_test_success(self, mock_llm_class, client):
        """Test successful LLM connection test on index page"""
        mock_llm = MagicMock()
        mock_response = Mock()
        mock_response.content = "Python is a high-level programming language known for its simplicity."
        mock_llm.invoke.return_value = mock_response
        mock_llm_class.return_value = mock_llm
        
        response = client.get('/')
        assert response.status_code == 200
    
    def test_index_llm_test_failure(self, client):
        """Test LLM test failure handling on index page"""
        with patch('routes.ChatGoogleGenerativeAI', side_effect=Exception("API Error")):
            response = client.get('/')
            assert response.status_code == 200


class TestUploadDocuments:
    """Tests for document upload and processing"""
    
    def test_upload_documents_get(self, client):
        """Test GET request to upload documents page"""
        response = client.get('/upload_documents')
        assert response.status_code == 200
        assert b'upload' in response.data.lower()
    
    @patch('services.document_processor.initialize_vector_db')
    @patch('services.ats_analyzer.get_jd_keywords')
    @patch('services.ats_analyzer.calculate_ats_score')
    @patch('services.llm_chains.get_initial_question_chain')
    @patch('services.document_processor.load_and_split_file_document')
    def test_upload_documents_post_success(
        self, 
        mock_load_split, 
        mock_initial_q, 
        mock_ats_score, 
        mock_keywords, 
        mock_init_db,
        client, 
        sample_jd_text, 
        mock_document_chunks
    ):
        """Test successful document upload and processing"""
        # Setup mocks
        mock_load_split.return_value = mock_document_chunks
        mock_keywords.return_value = ['Python', 'Flask', 'REST API', 'SQL']
        mock_ats_score.return_value = (85, "Good match with relevant experience")
        
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = "Tell me about yourself and your background."
        mock_initial_q.return_value = mock_chain
        
        # Create file data
        data = {
            'resume': (io.BytesIO(b"Resume content"), 'resume.pdf'),
            'job_description_text': sample_jd_text
        }
        
        response = client.post(
            '/upload_documents',
            data=data,
            content_type='multipart/form-data',
            follow_redirects=True
        )
        
        assert response.status_code == 200
        
        # Verify session data
        with client.session_transaction() as sess:
            assert 'ats_results' in sess
            assert 'interview_history' in sess
            assert sess['current_stage'] == 'FOUNDATIONAL_WARMUP'
    
    def test_upload_documents_no_resume(self, client, sample_jd_text):
        """Test upload without resume file"""
        data = {
            'job_description_text': sample_jd_text
        }
        
        response = client.post(
            '/upload_documents',
            data=data,
            follow_redirects=True
        )
        
        assert response.status_code == 200
        assert b'Resume file is required' in response.data
    
    def test_upload_documents_no_jd(self, client):
        """Test upload without job description"""
        data = {
            'resume': (io.BytesIO(b"Resume content"), 'resume.pdf'),
            'job_description_text': ''
        }
        
        response = client.post(
            '/upload_documents',
            data=data,
            content_type='multipart/form-data',
            follow_redirects=True
        )
        
        assert response.status_code == 200
        assert b'Job Description text cannot be empty' in response.data
    
    def test_upload_documents_invalid_file_type(self, client, sample_jd_text):
        """Test upload with invalid file type"""
        data = {
            'resume': (io.BytesIO(b"Resume content"), 'resume.txt'),
            'job_description_text': sample_jd_text
        }
        
        response = client.post(
            '/upload_documents',
            data=data,
            content_type='multipart/form-data',
            follow_redirects=True
        )
        
        assert response.status_code == 200
        assert b'Only PDF and DOCX files are allowed' in response.data


class TestInterviewFlow:
    """Tests for the interview flow and question generation"""
    
    def test_start_interview_without_documents(self, client):
        """Test starting interview without uploading documents"""
        response = client.get('/start_interview', follow_redirects=True)
        assert response.status_code == 200
        assert b'Please upload documents first' in response.data
    
    def test_start_interview_with_session(self, session_with_interview):
        """Test starting interview with valid session"""
        with patch('services.document_processor.get_vector_store', return_value=MagicMock()):
            response = session_with_interview.get('/start_interview')
            assert response.status_code == 200
    
    @patch('services.interview_manager.get_next_question')
    @patch('services.interview_manager.analyze_and_feedback_answer')
    @patch('services.document_processor.get_vector_store')
    def test_interview_flow_post_success(
        self, 
        mock_get_db, 
        mock_analyze, 
        mock_next_q,
        session_with_interview
    ):
        """Test successful interview flow with answer submission"""
        # Setup mocks
        mock_get_db.return_value = MagicMock()
        mock_analyze.return_value = (
            "Good answer! You demonstrated relevant experience.",
            "CONTINUE"
        )
        mock_next_q.return_value = (
            "Can you explain your experience with REST APIs?",
            "CONTINUE"
        )
        
        data = {
            'user_answer': 'I have 5 years of experience working with Python and Flask.'
        }
        
        response = session_with_interview.post(
            '/interview_flow',
            data=data,
            follow_redirects=False
        )
        
        assert response.status_code == 302  # Redirect
        
        # Verify the interview history was updated
        with session_with_interview.session_transaction() as sess:
            assert len(sess['interview_history']) == 2  # Original + new question
    
    @patch('services.interview_manager.analyze_and_feedback_answer')
    @patch('services.document_processor.get_vector_store')
    def test_interview_flow_end_interview(
        self, 
        mock_get_db, 
        mock_analyze,
        session_with_interview
    ):
        """Test interview ending based on analysis"""
        mock_get_db.return_value = MagicMock()
        mock_analyze.return_value = (
            "This answer is inappropriate for a professional interview.",
            "END_INTERVIEW"
        )
        
        data = {
            'user_answer': 'I dont want to answer this question.'
        }
        
        response = session_with_interview.post(
            '/interview_flow',
            data=data,
            follow_redirects=True
        )
        
        assert response.status_code == 200
        assert b'Interview' in response.data
    
    def test_interview_flow_no_answer(self, session_with_interview):
        """Test interview flow without providing an answer"""
        with patch('services.document_processor.get_vector_store', return_value=MagicMock()):
            response = session_with_interview.post(
                '/interview_flow',
                data={'user_answer': ''},
                follow_redirects=False
            )
            
            assert response.status_code == 200
            assert b'Please provide an answer' in response.data
    
    def test_interview_flow_no_session(self, client):
        """Test interview flow without session data"""
        response = client.post(
            '/interview_flow',
            data={'user_answer': 'Test answer'},
            follow_redirects=True
        )
        
        assert response.status_code == 200
        assert b'Interview session lost' in response.data or b'upload documents' in response.data.lower()


class TestEndInterview:
    """Tests for ending interview and cleanup"""
    
    @patch('services.document_processor.clear_vector_db')
    def test_end_interview(self, mock_clear_db, session_with_interview):
        """Test interview cleanup on end"""
        response = session_with_interview.get('/end_interview', follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Interview ended' in response.data or b'upload' in response.data.lower()
        
        # Verify session was cleared
        with session_with_interview.session_transaction() as sess:
            assert 'interview_history' not in sess
            assert 'ats_results' not in sess
            assert 'current_stage' not in sess
        
        # Verify cleanup was called
        mock_clear_db.assert_called_once()


class TestSessionManagement:
    """Tests for session and state management"""
    
    @patch('services.document_processor.initialize_vector_db')
    @patch('services.ats_analyzer.get_jd_keywords')
    @patch('services.ats_analyzer.calculate_ats_score')
    @patch('services.llm_chains.get_initial_question_chain')
    @patch('services.document_processor.load_and_split_file_document')
    def test_session_state_persistence(
        self,
        mock_load_split,
        mock_initial_q,
        mock_ats_score,
        mock_keywords,
        mock_init_db,
        client,
        sample_jd_text,
        mock_document_chunks
    ):
        """Test that session state persists correctly across requests"""
        # Setup mocks
        mock_load_split.return_value = mock_document_chunks
        mock_keywords.return_value = ['Python', 'Flask']
        mock_ats_score.return_value = (85, "Good match")
        
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = "Tell me about yourself."
        mock_initial_q.return_value = mock_chain
        
        # Upload documents
        data = {
            'resume': (io.BytesIO(b"Resume content"), 'resume.pdf'),
            'job_description_text': sample_jd_text
        }
        
        client.post(
            '/upload_documents',
            data=data,
            content_type='multipart/form-data',
            follow_redirects=True
        )
        
        # Verify session data
        with client.session_transaction() as sess:
            assert sess['current_stage'] == 'FOUNDATIONAL_WARMUP'
            assert sess['stage_question_count'] == 0
            assert 'ats_results' in sess
            assert 'interview_history' in sess


class TestErrorHandling:
    """Tests for error handling and edge cases"""
    
    @patch('services.document_processor.load_and_split_file_document')
    def test_upload_with_processing_error(self, mock_load, client, sample_jd_text):
        """Test handling of document processing errors"""
        mock_load.side_effect = Exception("Failed to process document")
        
        data = {
            'resume': (io.BytesIO(b"Resume content"), 'resume.pdf'),
            'job_description_text': sample_jd_text
        }
        
        response = client.post(
            '/upload_documents',
            data=data,
            content_type='multipart/form-data',
            follow_redirects=True
        )
        
        assert response.status_code == 200
        assert b'Error processing files' in response.data
    
    def test_allowed_file_function(self, client):
        """Test file extension validation"""
        from routes import allowed_file
        
        assert allowed_file('resume.pdf') == True
        assert allowed_file('resume.docx') == True
        assert allowed_file('resume.txt') == False
        assert allowed_file('resume.doc') == False
        assert allowed_file('resume') == False

