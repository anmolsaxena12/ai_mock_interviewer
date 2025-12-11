# Testing Guide for AI Mock Interviewer

This document provides comprehensive instructions on how to run tests for the AI Mock Interviewer application. The project includes both **integration tests** (pytest) and **end-to-end tests** (WebdriverIO).

## Table of Contents

1. [Test Overview](#test-overview)
2. [Prerequisites](#prerequisites)
3. [Setup](#setup)
4. [Running Integration Tests (Pytest)](#running-integration-tests-pytest)
5. [Running E2E Tests (WDIO)](#running-e2e-tests-wdio)
6. [Test Structure](#test-structure)
7. [Writing New Tests](#writing-new-tests)
8. [Continuous Integration](#continuous-integration)
9. [Troubleshooting](#troubleshooting)

---

## Test Overview

### Integration Tests (Pytest)
- **Location**: `tests/`
- **Framework**: pytest
- **Purpose**: Test backend logic, API endpoints, and service layer functionality
- **Mock**: External dependencies (LLM, ChromaDB) are mocked for fast, reliable tests

### End-to-End Tests (WDIO)
- **Location**: `test/`
- **Framework**: WebdriverIO v8
- **Purpose**: Test complete user workflows through the browser
- **Scope**: Navigation, file uploads, form submissions, interview flow

---

## Prerequisites

### For Integration Tests (Pytest)
- Python 3.8+
- pip

### For E2E Tests (WDIO)
- Node.js 14+ and npm
- Chrome browser (for local testing)

---

## Setup

### 1. Install Python Dependencies

```bash
# Create and activate virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install requirements including test dependencies
pip install -r requirements.txt
```

### 2. Install Node.js Dependencies

```bash
# Install WDIO and related packages
npm install
```

### 3. Environment Configuration

Create a `.env` file in the project root:

```bash
# Required for integration tests (can be mock value for testing)
GOOGLE_API_KEY=your_test_api_key_here
FLASK_SECRET_KEY=test_secret_key_for_sessions
```

**Note**: For integration tests, the Google API key can be a dummy value since LLM calls are mocked.

---

## Running Integration Tests (Pytest)

### Run All Integration Tests

```bash
pytest
```

### Run with Verbose Output

```bash
pytest -v
```

### Run Specific Test File

```bash
pytest tests/test_routes.py
pytest tests/test_services.py
```

### Run Specific Test Class or Function

```bash
# Run a specific test class
pytest tests/test_routes.py::TestIndexRoute

# Run a specific test function
pytest tests/test_routes.py::TestIndexRoute::test_index_page_loads
```

### Run Tests with Coverage

```bash
# Install coverage if not already installed
pip install pytest-cov

# Run tests with coverage report
pytest --cov=. --cov-report=html --cov-report=term

# View HTML coverage report
open htmlcov/index.html  # On macOS
# or
xdg-open htmlcov/index.html  # On Linux
```

### Run Tests by Markers

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Skip slow tests
pytest -m "not slow"
```

### Pytest Options

```bash
# Stop on first failure
pytest -x

# Show local variables in tracebacks
pytest -l

# Capture output (print statements)
pytest -s

# Run tests in parallel (requires pytest-xdist)
pip install pytest-xdist
pytest -n auto
```

---

## Running E2E Tests (WDIO)

### Start the Application First

Before running E2E tests, ensure the Flask application is running:

```bash
# In a separate terminal
python app.py
# Application should be running on http://localhost:5000
```

### Run All E2E Tests

```bash
npm test
# or
npx wdio run wdio.conf.js
```

### Run Specific Test File

```bash
npx wdio run wdio.conf.js --spec test/specs/navigation.e2e.js
```

### Run in Non-Headless Mode (See Browser)

Edit `wdio.conf.js` and remove or comment out the `--headless` flag:

```javascript
'goog:chromeOptions': {
    args: [
        // '--headless',  // Comment this out
        '--disable-gpu',
        '--window-size=1920,1080'
    ]
}
```

### WDIO Watch Mode

```bash
# Install wdio watch service
npm install --save-dev @wdio/watch-service

# Run in watch mode (re-run tests on file changes)
npx wdio run wdio.conf.js --watch
```

---

## Test Structure

### Integration Tests Structure

```
tests/
├── __init__.py
├── test_routes.py          # Tests for Flask routes and endpoints
└── test_services.py        # Tests for service layer (ATS, document processing, etc.)

conftest.py                 # Pytest fixtures and configuration
pytest.ini                  # Pytest settings
```

### E2E Tests Structure

```
test/
├── pageobjects/
│   ├── base.page.js        # Base page object with common methods
│   ├── index.page.js       # Home page object
│   ├── upload.page.js      # Upload documents page object
│   └── interview.page.js   # Interview page object
└── specs/
    └── navigation.e2e.js   # Navigation and basic flow tests

wdio.conf.js                # WebdriverIO configuration
```

---

## Test Coverage

### What's Tested

#### Integration Tests
- ✅ Route handlers and HTTP responses
- ✅ Document upload and validation
- ✅ ATS scoring and keyword extraction
- ✅ Interview flow and state management
- ✅ Session handling
- ✅ Error handling and edge cases
- ✅ Service layer functions
- ✅ Document processing and chunking
- ✅ Vector database operations (mocked)

#### E2E Tests
- ✅ Page navigation and loading
- ✅ UI element visibility
- ✅ Form interactions
- ✅ File upload workflows
- ✅ Error message display
- ✅ Success flows

---

## Writing New Tests

### Writing a New Integration Test

```python
# tests/test_new_feature.py
import pytest
from unittest.mock import patch, MagicMock

class TestNewFeature:
    """Tests for new feature"""
    
    def test_new_functionality(self, client):
        """Test description"""
        # Arrange
        test_data = {'key': 'value'}
        
        # Act
        response = client.post('/endpoint', data=test_data)
        
        # Assert
        assert response.status_code == 200
        assert b'expected_content' in response.data
    
    @patch('services.some_module.some_function')
    def test_with_mock(self, mock_function, client):
        """Test with mocked dependency"""
        mock_function.return_value = "mocked_result"
        
        response = client.get('/endpoint')
        
        assert response.status_code == 200
        mock_function.assert_called_once()
```

### Writing a New E2E Test

```javascript
// test/specs/new-feature.e2e.js
const NewPage = require('../pageobjects/newpage.page');

describe('New Feature Tests', () => {
    it('should perform new action', async () => {
        // Arrange
        await NewPage.open();
        
        // Act
        await NewPage.performAction();
        
        // Assert
        await expect(NewPage.resultElement).toBeDisplayed();
    });
});
```

### Creating a New Page Object

```javascript
// test/pageobjects/newpage.page.js
const BasePage = require('./base.page');

class NewPage extends BasePage {
    get someElement() {
        return $('#element-id');
    }
    
    async open() {
        await super.open('/new-page');
        await this.waitForPageLoad();
    }
    
    async performAction() {
        await this.clickElement(this.someElement);
    }
}

module.exports = new NewPage();
```

---

## Continuous Integration

### GitHub Actions Example

Create `.github/workflows/tests.yml`:

```yaml
name: Run Tests

on: [push, pull_request]

jobs:
  integration-tests:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Run pytest
      env:
        GOOGLE_API_KEY: ${{ secrets.GOOGLE_API_KEY }}
      run: |
        pytest --cov=. --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
  
  e2e-tests:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
    
    - name: Install dependencies
      run: npm install
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install Python dependencies
      run: pip install -r requirements.txt
    
    - name: Start Flask app
      run: |
        python app.py &
        sleep 5
      env:
        GOOGLE_API_KEY: ${{ secrets.GOOGLE_API_KEY }}
    
    - name: Run WDIO tests
      run: npm test
```

---

## Troubleshooting

### Common Issues and Solutions

#### Integration Tests

**Issue**: `ModuleNotFoundError: No module named 'app'`
```bash
# Solution: Ensure you're in the project root and PYTHONPATH is set
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
pytest
```

**Issue**: Tests fail due to missing `.env`
```bash
# Solution: Create .env file or export variables
export GOOGLE_API_KEY=test_key
export FLASK_SECRET_KEY=test_secret
pytest
```

**Issue**: ChromaDB persistence errors
```bash
# Solution: Clean up test databases
rm -rf test_chroma_db/
rm -rf test_uploads/
pytest
```

#### E2E Tests

**Issue**: `Error: ChromeDriver not found`
```bash
# Solution: Install chromedriver service
npm install --save-dev wdio-chromedriver-service
```

**Issue**: `ECONNREFUSED: Connection refused to localhost:5000`
```bash
# Solution: Ensure Flask app is running
python app.py
# In another terminal:
npm test
```

**Issue**: Tests timeout waiting for elements
```bash
# Solution: Increase timeout in wdio.conf.js
waitforTimeout: 20000,  // Increase from 10000
```

**Issue**: Headless Chrome crashes
```bash
# Solution: Add these Chrome options in wdio.conf.js
'goog:chromeOptions': {
    args: [
        '--headless',
        '--disable-gpu',
        '--no-sandbox',
        '--disable-dev-shm-usage',
        '--disable-software-rasterizer'
    ]
}
```

#### File Upload Tests

**Issue**: File not found for upload tests
```bash
# Solution: Create test fixtures directory
mkdir -p test/fixtures
# Add sample PDF/DOCX files to test/fixtures/
```

---

## Test Data and Fixtures

### Sample Test Files

Create test fixtures in `test/fixtures/`:

```bash
mkdir -p test/fixtures
```

Sample files needed:
- `test/fixtures/sample_resume.pdf` - Valid resume PDF
- `test/fixtures/sample_resume.docx` - Valid resume DOCX
- `test/fixtures/invalid_file.txt` - Invalid file type for testing

### Mock Data

Test data is defined in `conftest.py`:
- `sample_jd_text` - Sample job description
- `sample_resume_content` - Sample resume content
- `mock_document_chunks` - Sample document chunks

---

## Running Tests in Docker

### Dockerfile for Testing

```dockerfile
FROM python:3.9-slim

# Install Node.js for WDIO tests
RUN apt-get update && apt-get install -y nodejs npm chromium

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY package.json package-lock.json ./
RUN npm install

COPY . .

ENV PYTHONPATH=/app
ENV GOOGLE_API_KEY=test_key

CMD ["pytest"]
```

### Run Tests in Docker

```bash
docker build -t ai-interviewer-tests .
docker run ai-interviewer-tests pytest
```

---

## Performance Testing

### Benchmark Tests

```bash
# Install pytest-benchmark
pip install pytest-benchmark

# Run benchmark tests
pytest --benchmark-only
```

---

## Test Reporting

### Generate HTML Report

```bash
# Install pytest-html
pip install pytest-html

# Generate HTML report
pytest --html=report.html --self-contained-html

# Open report
open report.html
```

### Generate JUnit XML (for CI)

```bash
pytest --junitxml=junit.xml
```

---

## Best Practices

1. **Keep tests isolated**: Each test should be independent
2. **Mock external dependencies**: Don't call real APIs in tests
3. **Use descriptive names**: Test names should describe what they test
4. **Follow AAA pattern**: Arrange, Act, Assert
5. **Clean up after tests**: Remove test files and reset state
6. **Test edge cases**: Include error conditions and boundary values
7. **Keep tests fast**: Mock slow operations
8. **Use fixtures**: Reuse common test setup
9. **Document tests**: Add docstrings explaining what tests verify

---

## Additional Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [WebdriverIO Documentation](https://webdriver.io/)
- [Flask Testing Guide](https://flask.palletsprojects.com/en/latest/testing/)
- [Page Object Pattern](https://webdriver.io/docs/pageobjects/)

---

## Support

If you encounter issues with tests:
1. Check the troubleshooting section above
2. Ensure all dependencies are installed
3. Verify environment variables are set
4. Check that the Flask app is running (for E2E tests)
5. Review test logs for specific error messages

---

**Last Updated**: November 2025
