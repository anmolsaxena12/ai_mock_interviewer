"""
Tests for new features: audio interviews and coding challenges.
"""
import pytest
import json
from unittest.mock import patch, MagicMock


class TestCodingChallengeRoutes:
    """Tests for coding challenge routes"""
    
    def test_coding_challenge_page_loads(self, client):
        """Test that coding challenge page loads"""
        with client.session_transaction() as sess:
            sess['current_problem_id'] = 1
        
        response = client.get('/coding_challenge')
        assert response.status_code == 200
    
    def test_coding_challenge_random_problem(self, client):
        """Test random problem selection"""
        response = client.get('/coding_challenge')
        assert response.status_code == 200
        
        # Check that a problem was assigned to session
        with client.session_transaction() as sess:
            assert 'current_problem_id' in sess
    
    @patch('services.code_executor.CodeExecutor')
    def test_run_code_python(self, mock_executor_class, client):
        """Test running Python code"""
        # Setup mock
        mock_executor = MagicMock()
        mock_executor.execute.return_value = {
            'output': '[0,1]',
            'error': None,
            'exit_code': 0
        }
        mock_executor_class.return_value = mock_executor
        
        data = {
            'code': 'print("test")',
            'language': 'python',
            'problem_id': 1
        }
        
        response = client.post(
            '/run_code',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        result = json.loads(response.data)
        assert 'output' in result
    
    def test_run_code_missing_data(self, client):
        """Test run code with missing data"""
        data = {'code': 'print("test")'}  # Missing language
        
        response = client.post(
            '/run_code',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
    
    @patch('services.code_executor.CodeExecutor')
    def test_submit_code_all_pass(self, mock_executor_class, client):
        """Test submitting code with all tests passing"""
        # Setup mock
        mock_executor = MagicMock()
        mock_executor.execute.return_value = {
            'output': '[0,1]',
            'error': None,
            'exit_code': 0
        }
        mock_executor_class.return_value = mock_executor
        
        data = {
            'code': 'def twoSum(nums, target): return [0,1]',
            'language': 'python',
            'problem_id': 1,
            'time_taken': 120
        }
        
        response = client.post(
            '/submit_code',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        result = json.loads(response.data)
        assert 'test_results' in result
        assert 'all_passed' in result
    
    @patch('services.code_executor.CodeExecutor')
    def test_submit_code_with_failure(self, mock_executor_class, client):
        """Test submitting code with test failures"""
        # Setup mock
        mock_executor = MagicMock()
        mock_executor.execute.return_value = {
            'output': '[1,0]',  # Wrong answer
            'error': None,
            'exit_code': 0
        }
        mock_executor_class.return_value = mock_executor
        
        data = {
            'code': 'def twoSum(nums, target): return [1,0]',
            'language': 'python',
            'problem_id': 1,
            'time_taken': 120
        }
        
        response = client.post(
            '/submit_code',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result['all_passed'] == False
    
    def test_change_problem(self, client):
        """Test changing to different problem"""
        response = client.get('/change_problem/2', follow_redirects=False)
        assert response.status_code == 302  # Redirect
        
        with client.session_transaction() as sess:
            assert sess.get('current_problem_id') == 2
    
    def test_change_invalid_problem(self, client):
        """Test changing to non-existent problem"""
        response = client.get('/change_problem/999', follow_redirects=True)
        assert response.status_code == 200
        assert b'Problem not found' in response.data


class TestAudioInterviewFeatures:
    """Tests for audio interview features"""
    
    def test_interview_page_has_audio_controls(self, session_with_interview):
        """Test that interview page includes audio controls"""
        with patch('services.document_processor.get_vector_store', return_value=MagicMock()):
            response = session_with_interview.get('/start_interview')
            assert response.status_code == 200
            # Check for audio mode toggle
            assert b'audioMode' in response.data or b'Audio' in response.data
    
    def test_interview_flow_with_transcribed_answer(self, session_with_interview):
        """Test interview flow with audio transcribed answer"""
        with patch('services.document_processor.get_vector_store', return_value=MagicMock()):
            with patch('services.interview_manager.analyze_and_feedback_answer') as mock_analyze:
                with patch('services.interview_manager.get_next_question') as mock_next_q:
                    mock_analyze.return_value = ("Good answer", "CONTINUE")
                    mock_next_q.return_value = ("Next question?", "CONTINUE")
                    
                    # Simulate audio transcribed answer
                    data = {
                        'user_answer': 'I have extensive experience with Python and machine learning.'
                    }
                    
                    response = session_with_interview.post(
                        '/interview_flow',
                        data=data,
                        follow_redirects=False
                    )
                    
                    assert response.status_code == 302


class TestProblemsService:
    """Tests for problems service"""
    
    def test_get_problem_by_id(self):
        """Test getting problem by ID"""
        from services import problems
        
        problem = problems.get_problem(1)
        assert problem is not None
        assert problem['id'] == 1
        assert problem['title'] == "Two Sum"
        assert 'starter_code' in problem
        assert 'test_cases' in problem
    
    def test_get_nonexistent_problem(self):
        """Test getting non-existent problem"""
        from services import problems
        
        problem = problems.get_problem(999)
        assert problem is None
    
    def test_get_all_problems(self):
        """Test getting all problems"""
        from services import problems
        
        all_problems = problems.get_all_problems()
        assert len(all_problems) > 0
        assert all(isinstance(p, dict) for p in all_problems)
        assert all('id' in p for p in all_problems)
    
    def test_problem_has_required_fields(self):
        """Test that problems have all required fields"""
        from services import problems
        
        problem = problems.get_problem(1)
        required_fields = [
            'id', 'title', 'difficulty', 'category', 'description',
            'examples', 'constraints', 'starter_code', 'test_cases'
        ]
        
        for field in required_fields:
            assert field in problem, f"Problem missing required field: {field}"
    
    def test_starter_code_for_all_languages(self):
        """Test that starter code exists for all languages"""
        from services import problems
        
        problem = problems.get_problem(1)
        languages = ['python', 'cpp', 'java']
        
        for lang in languages:
            assert lang in problem['starter_code']
            assert len(problem['starter_code'][lang]) > 0
    
    def test_get_random_problem(self):
        """Test getting random problem"""
        from services import problems
        
        problem = problems.get_random_problem()
        assert problem is not None
        assert 'id' in problem


class TestSessionPersistence:
    """Tests for session management with new features"""
    
    def test_session_stores_code_submissions(self, client):
        """Test that code submissions are stored in session"""
        with client.session_transaction() as sess:
            sess['code_submissions'] = []
        
        with patch('services.code_executor.CodeExecutor') as mock_executor_class:
            mock_executor = MagicMock()
            mock_executor.execute.return_value = {
                'output': '[0,1]',
                'error': None,
                'exit_code': 0
            }
            mock_executor_class.return_value = mock_executor
            
            data = {
                'code': 'solution code',
                'language': 'python',
                'problem_id': 1,
                'time_taken': 120
            }
            
            client.post(
                '/submit_code',
                data=json.dumps(data),
                content_type='application/json'
            )
            
            with client.session_transaction() as sess:
                assert 'code_submissions' in sess
                assert len(sess['code_submissions']) > 0
    
    def test_problem_id_persists_in_session(self, client):
        """Test that current problem ID persists"""
        response = client.get('/coding_challenge')
        
        with client.session_transaction() as sess:
            problem_id = sess.get('current_problem_id')
        
        # Access again
        response = client.get('/coding_challenge')
        
        with client.session_transaction() as sess:
            assert sess.get('current_problem_id') == problem_id


class TestIntegrationWithInterview:
    """Test integration between interview and coding challenge"""
    
    def test_navigation_from_interview_to_coding(self, session_with_interview):
        """Test navigating from interview to coding challenge"""
        with patch('services.document_processor.get_vector_store', return_value=MagicMock()):
            response = session_with_interview.get('/start_interview')
            assert b'coding' in response.data.lower() or b'code' in response.data.lower()
    
    def test_session_maintains_both_states(self, client):
        """Test that session can maintain both interview and coding state"""
        with client.session_transaction() as sess:
            sess['interview_history'] = [{"question": "Q1", "answer": "A1", "feedback": None}]
            sess['current_problem_id'] = 1
            sess['code_submissions'] = []
        
        # Both should be accessible
        with client.session_transaction() as sess:
            assert 'interview_history' in sess
            assert 'current_problem_id' in sess
            assert 'code_submissions' in sess


