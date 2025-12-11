# AI Mock Interviewer 🎯

AI-Powered Mock Interviewer with Adaptive Generative AI, Audio Interviews, and Coding Challenges

## 🚀 Features

### 1. Intelligent Interview System
- **Adaptive Question Generation**: Dynamic questions based on resume and job description using Google Gemini (GenAI)
- **Real-time Answer Analysis**: Instant feedback on interview responses
- **ATS Score Calculation**: Applicant Tracking System matching score
- **Multiple Interview Stages**: Warm-up, foundational, and JD/Resume-specific questions

### 2. Audio-Based Interviews 🎤
- **Speech-to-Text**: Record answers using your voice
- **Text-to-Speech**: Hear questions read aloud
- **Dual Mode**: Switch between text and audio input seamlessly
- **Browser-based**: No external API calls required

### 3. Coding Challenge Platform 💻
- **Multi-Language Support**: Python, C++, and Java
- **Monaco Editor**: VS Code-style code editor with syntax highlighting
- **Secure Code Execution**: Sandboxed environment with timeout limits
- **Instant Feedback**: Run code and submit solutions with test case validation
- **LeetCode-style Problems**: Array, String, Stack, and more categories

## 🛠 Technology Stack

- **Backend**: Flask (Python)
- **AI/ML**: LangChain, Google Gemini LLM, ChromaDB, HuggingFace Embeddings
- **Document Processing**: PyPDF2, docx2txt, RecursiveCharacterTextSplitter
- **Code Execution**: Subprocess with sandboxing (Python, g++, javac)
- **Frontend**: Bootstrap 5, Monaco Editor, Web Speech API
- **Testing**: Pytest, WebdriverIO

## 📋 Prerequisites

- Python 3.8+
- Node.js 14+ (for WDIO tests)
- Google API Key (for Gemini LLM)
- Optional: g++ compiler (for C++ execution)
- Optional: Java JDK (for Java execution)

## 🔧 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/ai_mock_interviewer.git
cd ai_mock_interviewer
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
npm install  # For WDIO tests
```

### 4. Set Up Environment Variables

Create a `.env` file in the project root:

```bash
GOOGLE_API_KEY=your_gemini_api_key_here
FLASK_SECRET_KEY=your_random_secret_key_here
```

Get your Google API key from: https://makersuite.google.com/app/apikey

### 5. Install Compilers (Optional)

For C++ and Java code execution:

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install g++ default-jdk
```

**macOS:**
```bash
brew install gcc
brew install openjdk
```

## 🎮 Usage

### Starting the Application

```bash
python app.py
```

The application will be available at `http://localhost:5000`

### Using the Interview Feature

1. **Upload Documents**
   - Navigate to the upload page
   - Upload your resume (PDF or DOCX)
   - Paste the job description
   - View your ATS score and missing keywords

2. **Start Interview**
   - Click "Start Interview"
   - Choose between Text or Audio mode
   - Answer questions
   - Receive instant feedback

3. **Audio Mode**
   - Toggle to Audio mode
   - Click "Hear Question" to listen
   - Click "Start Recording" to answer
   - Review transcription and submit

### Using the Coding Challenge

1. **Access Coding Challenge**
   - Click "Go to Coding Challenge" from interview page
   - Or navigate from home page

2. **Solve Problems**
   - Read problem description and examples
   - Select programming language (Python/C++/Java)
   - Write your solution in the editor
   - Click "Run Code" to test with sample inputs
   - Click "Submit" to run all test cases

3. **View Results**
   - See which test cases passed/failed
   - View expected vs actual output
   - Debug and resubmit

## 🧪 Testing

### Run Integration Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=. --cov-report=html

# Specific test file
pytest tests/test_code_executor.py -v
```

### Run E2E Tests

```bash
# Start the app first
python app.py

# In another terminal
npm test
```

See [TESTING.md](TESTING.md) for comprehensive testing documentation.

## 📁 Project Structure

```
ai_mock_interviewer/
├── app.py                      # Application factory
├── routes.py                   # Route handlers
├── config.py                   # Configuration
├── requirements.txt            # Python dependencies
├── package.json                # Node dependencies
│
├── services/                   # Service layer
│   ├── ats_analyzer.py        # ATS scoring
│   ├── document_processor.py  # Document handling
│   ├── interview_manager.py   # Interview logic
│   ├── llm_chains.py          # LLM prompt chains
│   ├── code_executor.py       # Code execution
│   └── problems.py            # Coding problems database
│
├── templates/                  # HTML templates
│   ├── index.html             # Home page
│   ├── upload_documents.html  # Upload page
│   ├── interview.html         # Interview page (with audio)
│   └── coding_challenge.html  # Coding editor page
│
├── tests/                      # Test suite
│   ├── conftest.py            # Test fixtures
│   ├── test_routes.py         # Route tests
│   ├── test_services.py       # Service tests
│   ├── test_code_executor.py  # Code execution tests
│   └── test_new_features.py   # New features tests
│
├── test/                       # WDIO E2E tests
│   ├── pageobjects/           # Page object models
│   └── specs/                 # Test specifications
│
└── uploads/                    # Temporary upload folder
```

## 🎯 Key Features Details

### RAG System
- **Retrieval**: ChromaDB vector store with HuggingFace embeddings
- **Augmentation**: Context-aware question generation
- **Generation**: Google Gemini LLM for dynamic responses

### Interview Stages
1. **Foundational/Warmup**: General questions to start
2. **JD/Resume Specific**: Targeted questions based on documents
3. **Adaptive Pivoting**: Behavioral or foundational questions based on answers

### Code Execution Security
- Sandboxed execution environment
- 5-second timeout limit
- 256MB memory limit
- Process isolation
- Automatic cleanup

## 📚 Documentation

- [TESTING.md](TESTING.md) - Comprehensive testing guide
- [NEW_FEATURES.md](NEW_FEATURES.md) - Detailed feature documentation
- [TEST_SUMMARY.md](TEST_SUMMARY.md) - Test overview

## 🔐 Security Considerations

- Resume/JD data is processed locally
- Code execution is sandboxed
- No data persistence (session-based)
- API keys stored in environment variables
- Input validation and sanitization

## 🚧 Known Limitations

- Speech recognition works best in Chrome and Safari
- Code execution requires system compilers for C++/Java
- LLM requires internet connection and API key
- Session data is not persisted

## 🛣 Roadmap

- [ ] More coding problems (50+ problems)
- [ ] Multiple interview templates
- [ ] Progress tracking and analytics
- [ ] Export interview reports
- [ ] Multi-language support (Spanish, French)
- [ ] Voice emotion analysis
- [ ] Code performance metrics
- [ ] Leaderboard for coding challenges

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Google Gemini for LLM capabilities
- LangChain for RAG framework
- Monaco Editor for code editing
- Bootstrap for UI components
- Web Speech API for audio features

## 📧 Contact

For questions or feedback, please open an issue on GitHub.

---

**Version**: 2.0.0  
**Last Updated**: November 2025

Made with ❤️ for job seekers and interview prep
