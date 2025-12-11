# Quick Start Guide - New Features

## 🎉 What's New?

Your AI Mock Interviewer now has **two major new features**:

1. **🎤 Audio-Based Interviews** - Speak your answers naturally
2. **💻 Coding Challenge Platform** - Solve LeetCode-style problems

---

## 🚀 Getting Started in 5 Minutes

### Step 1: Check Requirements

```bash
# Verify Python
python3 --version  # Should be 3.8+

# Verify Node (for tests)
node --version  # Should be 14+
```

### Step 2: Install Dependencies

```bash
# Install Python packages
pip install -r requirements.txt

# Optional: Install for coding challenges
# On macOS:
brew install gcc openjdk

# On Ubuntu:
sudo apt-get install g++ default-jdk
```

### Step 3: Set Up Environment

Create `.env` file:
```bash
GOOGLE_API_KEY=your_key_here
FLASK_SECRET_KEY=any_random_string
```

### Step 4: Run the Application

```bash
python app.py
```

Visit: `http://localhost:5000`

---

## 🎤 Using Audio Interviews

### Quick Start

1. Upload resume and job description
2. Click "Start Interview"
3. **Toggle to "Audio" mode** (top-right button)
4. Click "Hear Question" to listen
5. Click "Start Recording" to answer
6. Speak your answer naturally
7. Click "Stop Recording"
8. Review transcription
9. Click "Submit Audio Answer"

### Tips for Best Results

✅ **DO:**
- Use Chrome or Safari (best speech recognition)
- Speak clearly and naturally
- Minimize background noise
- Use a good quality microphone

❌ **DON'T:**
- Don't speak too fast
- Avoid mumbling
- Don't rely on it in noisy environments

### Troubleshooting

**"Speech recognition not supported"**
- Use Chrome or Safari browser
- Update your browser to latest version

**"Can't access microphone"**
- Grant microphone permissions
- Check browser settings
- Check system privacy settings

---

## 💻 Using Coding Challenges

### Quick Start

1. From interview page: Click "Go to Coding Challenge"
2. Or from home: Click "Try Coding Challenge"
3. Read the problem description
4. Select language: Python, C++, or Java
5. Write your solution
6. Click "Run Code" to test
7. Click "Submit" to validate

### Available Problems

| ID | Problem | Difficulty | Category |
|----|---------|------------|----------|
| 1 | Two Sum | Easy | Arrays |
| 2 | Reverse String | Easy | Strings |
| 3 | Valid Parentheses | Easy | Stack |

### Editor Features

- **Syntax Highlighting**: Automatic for all languages
- **Auto-completion**: Press Ctrl+Space
- **Find**: Ctrl/Cmd + F
- **Replace**: Ctrl/Cmd + H
- **Keyboard Shortcuts**:
  - `Ctrl/Cmd + Enter` - Run Code
  - `Ctrl/Cmd + S` - Submit Code

### Language-Specific Notes

#### Python
- Use Python 3
- Standard library available
- JSON module for input/output

#### C++
- C++17 standard
- Compiled with g++
- Include necessary headers

#### Java
- Java 11+
- Main class must be named `Solution`
- Use Scanner for input

### Example Solution

**Problem**: Two Sum

**Python:**
```python
def twoSum(nums, target):
    seen = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []
```

**C++:**
```cpp
vector<int> twoSum(vector<int>& nums, int target) {
    unordered_map<int, int> seen;
    for (int i = 0; i < nums.size(); i++) {
        int complement = target - nums[i];
        if (seen.count(complement)) {
            return {seen[complement], i};
        }
        seen[nums[i]] = i;
    }
    return {};
}
```

---

## 🧪 Testing Your Setup

### Test Audio Feature

1. Go to interview page
2. Toggle to Audio mode
3. Try "Hear Question" button
4. Try recording (should see transcription)

### Test Coding Challenge

1. Go to coding challenge
2. Select Python
3. Write: `print("Hello, World!")`
4. Click "Run Code"
5. Should see output in console

### Run Automated Tests

```bash
# Test code execution
pytest tests/test_code_executor.py -v

# Test new features
pytest tests/test_new_features.py -v

# All tests
pytest
```

---

## 📊 Feature Comparison

| Feature | Before | After |
|---------|--------|-------|
| **Interview Input** | Text only | Text + Audio |
| **Question Playback** | None | Text-to-Speech |
| **Coding Practice** | ❌ | ✅ 3 Languages |
| **Code Editor** | ❌ | ✅ Monaco Editor |
| **Test Cases** | ❌ | ✅ Automatic |

---

## 🎯 Typical Usage Flow

### Full Interview + Coding Session

```
1. Upload Resume & JD
   ↓
2. View ATS Score
   ↓
3. Start Interview (Text or Audio mode)
   ↓
4. Answer 5-7 questions
   ↓
5. Receive feedback after each answer
   ↓
6. Go to Coding Challenge
   ↓
7. Solve 1-3 problems
   ↓
8. End session
```

---

## 🛠 Customization

### Adding More Problems

Edit `services/problems.py`:

```python
PROBLEMS[4] = {
    "id": 4,
    "title": "Your Problem",
    "difficulty": "Medium",
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
    "test_cases": [...]
}
```

### Adjusting Timeouts

Edit `services/code_executor.py`:

```python
TIMEOUT = 5  # Change to desired seconds
MEMORY_LIMIT = 256  # Change to desired MB
```

### Changing Max Questions

Edit `config.py`:

```python
MAX_FOUNDATIONAL_QUESTIONS = 3  # Change as needed
```

---

## 🔒 Security Notes

- Code execution is sandboxed
- 5-second timeout prevents infinite loops
- No network access during execution
- Automatic cleanup of temporary files
- Speech processing happens in browser (client-side)
- No audio data sent to server

---

## 📱 Browser Compatibility

| Browser | Audio Interview | Coding Challenge |
|---------|----------------|------------------|
| Chrome  | ✅ Full Support | ✅ Full Support |
| Safari  | ✅ Full Support | ✅ Full Support |
| Firefox | ⚠️ Limited (no speech recognition) | ✅ Full Support |
| Edge    | ✅ Full Support | ✅ Full Support |

---

## 🐛 Common Issues & Solutions

### Issue: Audio not working

**Solution:**
1. Check browser compatibility (use Chrome/Safari)
2. Grant microphone permissions
3. Try refreshing the page

### Issue: Code execution fails

**Solution:**
1. Check if compiler is installed: `g++ --version` or `javac -version`
2. Check for syntax errors in code
3. Review error message in output console

### Issue: Tests failing

**Solution:**
1. Check expected output format
2. Ensure output matches exactly (including whitespace)
3. Use "Run Code" to debug first

### Issue: Session lost

**Solution:**
1. Don't close browser tab
2. Session expires after inactivity
3. Upload documents again if needed

---

## 📚 Learn More

- **Full Documentation**: See [NEW_FEATURES.md](NEW_FEATURES.md)
- **Testing Guide**: See [TESTING.md](TESTING.md)
- **API Reference**: See [NEW_FEATURES.md](NEW_FEATURES.md#api-reference)

---

## 🎓 Best Practices

### For Audio Interviews
1. Test your microphone first
2. Find a quiet environment
3. Speak naturally, not too fast
4. Review transcription before submitting
5. Have a backup (text mode) ready

### For Coding Challenges
1. Read the problem carefully
2. Check constraints and examples
3. Test with sample inputs first
4. Consider edge cases
5. Optimize after getting it working

---

## 💡 Pro Tips

1. **Combine Both Features**: Do interview first, then coding challenge
2. **Use Hints Wisely**: Only look at hints after trying yourself
3. **Time Yourself**: Treat it like a real interview
4. **Practice Regularly**: Use different problems
5. **Review Feedback**: Learn from interview feedback

---

## 🚀 Next Steps

1. ✅ Complete a full interview session
2. ✅ Try audio mode
3. ✅ Solve all 3 coding problems
4. ✅ Add your own custom problems
5. ✅ Share feedback and contribute!

---

## 📞 Need Help?

- 🐛 **Bug Reports**: Open an issue on GitHub
- 💬 **Questions**: Check documentation files
- 🤝 **Contributions**: Pull requests welcome!

---

**Happy Interviewing! 🎯**

*Remember: The more you practice, the better you'll perform in real interviews!*


