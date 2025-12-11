# New Features Guide

## Overview

This document describes the new features added to the AI Mock Interviewer application:
1. **Audio-Based Interviews** - Speech-to-text and text-to-speech capabilities
2. **Coding Challenge Platform** - LeetCode-style coding problems with multi-language support

---

## Feature 1: Audio-Based Interviews

### Description
Conduct interviews using voice input and audio playback of questions, making the interview experience more natural and hands-free.

### Key Features

#### 🎤 Speech-to-Text
- Real-time voice transcription
- Automatic conversion of spoken answers to text
- Support for continuous speech recognition

#### 🔊 Text-to-Speech
- Hear interview questions read aloud
- Adjustable speech rate and voice
- Play/pause controls

#### 🔀 Mode Switching
- Toggle between text and audio modes anytime
- Seamless transition between input methods
- Both modes available in the same interface

### How to Use

1. **Start an Interview**
   - Upload documents and begin interview as usual

2. **Switch to Audio Mode**
   - Click the "Audio" toggle button in the top-right corner
   - Grant microphone permissions when prompted

3. **Listen to Questions**
   - Click "Hear Question" button to have the question read aloud

4. **Record Your Answer**
   - Click "Start Recording" to begin
   - Speak your answer clearly
   - Click "Stop Recording" when finished
   - Review the transcription
   - Click "Play Recording" to hear your recording (optional)

5. **Submit**
   - Click "Submit Audio Answer" to continue

### Browser Compatibility

| Feature | Chrome | Firefox | Safari | Edge |
|---------|--------|---------|--------|------|
| Speech-to-Text | ✅ | ❌ | ✅ | ✅ |
| Text-to-Speech | ✅ | ✅ | ✅ | ✅ |
| Audio Recording | ✅ | ✅ | ✅ | ✅ |

**Note**: Speech recognition works best in Chrome and Safari.

### Technical Implementation

- **Web Speech API**: Native browser speech recognition
- **MediaRecorder API**: Audio recording
- **SpeechSynthesis API**: Text-to-speech conversion
- No external API calls required (runs entirely in browser)

### Tips for Best Results

- Use a good quality microphone
- Speak clearly and at a moderate pace
- Minimize background noise
- Use Chrome or Safari for best speech recognition
- Review transcription before submitting

---

## Feature 2: Coding Challenge Platform

### Description
A complete coding platform similar to LeetCode where candidates can solve programming problems in multiple languages with instant feedback.

### Key Features

#### 💻 Multi-Language Support
- **Python** - Full support with Python 3
- **C++** - C++17 standard with g++ compiler
- **Java** - Java 11+ support

#### ✨ Monaco Editor
- VS Code-style code editor
- Syntax highlighting
- Auto-completion
- Multiple themes
- Minimap for navigation

#### ⚡ Code Execution
- Secure sandboxed execution
- 5-second timeout limit
- Memory limit enforcement
- Real-time output display

#### ✅ Test Cases
- Sample test cases with examples
- Hidden test cases for submission
- Detailed pass/fail feedback
- Expected vs actual output comparison

#### 💡 Problem Features
- Difficulty ratings (Easy/Medium/Hard)
- Category tags
- Constraints
- Multiple examples
- Hints (optional)
- Detailed descriptions

### How to Use

1. **Access Coding Challenge**
   - From interview page, click "Go to Coding Challenge"
   - Or from home page, click "Try Coding Challenge"

2. **Read Problem**
   - Left panel shows problem description
   - Review examples and constraints
   - Use hints if needed (click "Show Hints")

3. **Select Language**
   - Choose from dropdown: Python, C++, or Java
   - Starter code template loads automatically

4. **Write Solution**
   - Write your code in the editor
   - Use the provided function signature
   - Don't modify input/output handling code

5. **Run Code**
   - Click "Run Code" to test with sample inputs
   - View output in the console below editor
   - Debug any errors

6. **Submit Solution**
   - Click "Submit" to run all test cases
   - View detailed results for each test case
   - See which tests passed/failed

### Available Problems

Currently includes 3 problems:

1. **Two Sum** (Easy) - Array problem using hash maps
2. **Reverse String** (Easy) - String manipulation with two pointers
3. **Valid Parentheses** (Easy) - Stack-based problem

More problems can be easily added to `services/problems.py`.

### Keyboard Shortcuts

- **Ctrl/Cmd + Enter**: Run code
- **Ctrl/Cmd + S**: Submit code
- **Ctrl/Cmd + Z**: Undo
- **Ctrl/Cmd + F**: Find
- **Ctrl/Cmd + H**: Replace

### Code Execution Flow

```
User Code → CodeExecutor Service → Temp File → Compile (if needed) → Execute → Capture Output → Compare with Expected → Return Results
```

### Security Features

- Sandboxed execution environment
- Timeout limits (5 seconds)
- Memory limits (256 MB)
- No network access
- Process isolation
- Automatic cleanup

### Technical Details

#### Backend Services

**`services/code_executor.py`**
- Handles code compilation and execution
- Supports Python, C++, and Java
- Implements timeout and resource limits
- Provides error handling and cleanup

**`services/problems.py`**
- Problem database
- Test cases
- Starter code templates
- Problem metadata

#### Routes

- `/coding_challenge` - Display problem page
- `/run_code` - Execute code with sample input
- `/submit_code` - Run all test cases
- `/change_problem/<id>` - Switch problems

### Adding New Problems

To add a new problem, edit `services/problems.py`:

```python
PROBLEMS[4] = {
    "id": 4,
    "title": "Your Problem Title",
    "difficulty": "Medium",  # Easy, Medium, or Hard
    "category": "Arrays",
    "description": """HTML description""",
    "examples": [...],
    "constraints": [...],
    "hints": [...],
    "starter_code": {
        "python": "...",
        "cpp": "...",
        "java": "..."
    },
    "test_cases": [
        {
            "input": ["..."],  # Array of input lines
            "expected_output": "..."
        }
    ]
}
```

### Troubleshooting

#### Code doesn't compile
- Check syntax errors in your code
- Ensure you're using correct language syntax
- For C++: Ensure you have g++ installed
- For Java: Ensure you have javac installed

#### Code times out
- Optimize your algorithm
- Avoid infinite loops
- Check time complexity

#### Test cases fail
- Print intermediate values to debug
- Check edge cases
- Ensure output format matches exactly

#### Permission errors
- On Linux/Mac: Ensure execute permissions
- May need to install compilers: `apt-get install g++ default-jdk`

---

## Integration with Interview Flow

The coding challenge can be accessed:
1. Directly from home page
2. From within an active interview
3. As a standalone feature

Session data is maintained across both features, allowing seamless switching between conversational interview and coding challenge.

---

## Future Enhancements

### Planned Features
- [ ] More problems (targeting 50+ problems)
- [ ] Problem difficulty filtering
- [ ] Category-based problem selection
- [ ] Code history and submissions tracking
- [ ] Performance metrics (time/space complexity)
- [ ] Leaderboard
- [ ] Code sharing
- [ ] Discussion forum
- [ ] Video explanations
- [ ] Premium problems

### Audio Feature Enhancements
- [ ] Multiple language support (Spanish, French, etc.)
- [ ] Voice activity detection
- [ ] Background noise cancellation
- [ ] Speaker verification
- [ ] Emotion analysis from voice

---

## API Reference

### Code Execution API

#### POST `/run_code`

Run code with sample test case.

**Request Body:**
```json
{
    "code": "def twoSum(nums, target): ...",
    "language": "python",
    "problem_id": 1,
    "test_type": "sample"
}
```

**Response:**
```json
{
    "output": "[0, 1]",
    "error": null,
    "test_input": "[2,7,11,15]\n9"
}
```

#### POST `/submit_code`

Submit solution and run all test cases.

**Request Body:**
```json
{
    "code": "def twoSum(nums, target): ...",
    "language": "python",
    "problem_id": 1,
    "time_taken": 245
}
```

**Response:**
```json
{
    "test_results": [
        {
            "input": "[2,7,11,15]\n9",
            "expected": "[0,1]",
            "actual": "[0,1]",
            "passed": true
        }
    ],
    "all_passed": true,
    "total_tests": 3,
    "passed_tests": 3
}
```

---

## Performance Considerations

### Code Execution
- Average execution time: < 500ms
- Compilation time (C++/Java): 1-3 seconds
- Resource cleanup is automatic
- Concurrent executions are isolated

### Audio Processing
- Speech recognition: Real-time
- Audio recording: No size limit
- Text-to-speech: Instant
- All processing happens client-side

---

## Configuration

### Code Execution Settings

Edit `services/code_executor.py`:

```python
# Timeout in seconds
TIMEOUT = 5

# Memory limit (in MB)
MEMORY_LIMIT = 256
```

### Problem Settings

Edit `config.py`:

```python
# Default problem for new sessions
DEFAULT_PROBLEM_ID = 1

# Enable/disable features
ENABLE_CODING_CHALLENGE = True
ENABLE_AUDIO_INTERVIEW = True
```

---

## Testing

### Testing Audio Features
- Manual testing required (browser-dependent)
- Test in Chrome, Firefox, Safari
- Test microphone permissions
- Test speech recognition accuracy

### Testing Code Execution
```bash
# Run code execution tests
pytest tests/test_code_executor.py -v

# Test specific language
pytest tests/test_code_executor.py::TestPythonExecution -v
```

### Testing Problems
```bash
# Verify all problems load correctly
python -c "from services.problems import get_all_problems; print(len(get_all_problems()))"
```

---

## License & Credits

- Monaco Editor: MIT License
- Web Speech API: W3C Standard
- Bootstrap Icons: MIT License

---

**Last Updated**: November 2025
**Version**: 2.0.0


