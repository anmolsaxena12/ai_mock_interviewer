"""
Tests for code execution service.

Tests the CodeExecutor class for Python, C++, and Java code execution.
"""
import pytest
from services.code_executor import CodeExecutor, CodeExecutionError


class TestPythonExecution:
    """Tests for Python code execution"""
    
    def test_simple_python_execution(self):
        """Test basic Python code execution"""
        executor = CodeExecutor()
        code = """
print("Hello, World!")
"""
        try:
            result = executor.execute(code, 'python')
            assert result['output'] == "Hello, World!"
            assert result['error'] is None
        finally:
            executor.cleanup()
    
    def test_python_with_input(self):
        """Test Python code with stdin input"""
        executor = CodeExecutor()
        code = """
name = input()
print(f"Hello, {name}!")
"""
        try:
            result = executor.execute(code, 'python', stdin_data="Alice")
            assert "Alice" in result['output']
        finally:
            executor.cleanup()
    
    def test_python_timeout(self):
        """Test Python code timeout"""
        executor = CodeExecutor()
        code = """
import time
time.sleep(10)
"""
        with pytest.raises(CodeExecutionError, match="Time Limit Exceeded"):
            executor.execute(code, 'python')
        executor.cleanup()
    
    def test_python_runtime_error(self):
        """Test Python runtime error handling"""
        executor = CodeExecutor()
        code = """
x = 1 / 0
"""
        with pytest.raises(CodeExecutionError, match="Runtime Error"):
            executor.execute(code, 'python')
        executor.cleanup()
    
    def test_python_import_error(self):
        """Test Python import error"""
        executor = CodeExecutor()
        code = """
import nonexistent_module
"""
        with pytest.raises(CodeExecutionError):
            executor.execute(code, 'python')
        executor.cleanup()


class TestCppExecution:
    """Tests for C++ code execution"""
    
    @pytest.mark.skipif(True, reason="Requires g++ compiler installed")
    def test_simple_cpp_execution(self):
        """Test basic C++ code execution"""
        executor = CodeExecutor()
        code = """
#include <iostream>
using namespace std;

int main() {
    cout << "Hello, World!" << endl;
    return 0;
}
"""
        try:
            result = executor.execute(code, 'cpp')
            assert result['output'] == "Hello, World!"
        finally:
            executor.cleanup()
    
    @pytest.mark.skipif(True, reason="Requires g++ compiler installed")
    def test_cpp_with_input(self):
        """Test C++ code with stdin input"""
        executor = CodeExecutor()
        code = """
#include <iostream>
#include <string>
using namespace std;

int main() {
    string name;
    cin >> name;
    cout << "Hello, " << name << "!" << endl;
    return 0;
}
"""
        try:
            result = executor.execute(code, 'cpp', stdin_data="Alice")
            assert "Alice" in result['output']
        finally:
            executor.cleanup()
    
    @pytest.mark.skipif(True, reason="Requires g++ compiler installed")
    def test_cpp_compilation_error(self):
        """Test C++ compilation error"""
        executor = CodeExecutor()
        code = """
#include <iostream>

int main() {
    cout << "Missing semicolon"
    return 0;
}
"""
        with pytest.raises(CodeExecutionError, match="Compilation Error"):
            executor.execute(code, 'cpp')
        executor.cleanup()


class TestJavaExecution:
    """Tests for Java code execution"""
    
    @pytest.mark.skipif(True, reason="Requires javac and java installed")
    def test_simple_java_execution(self):
        """Test basic Java code execution"""
        executor = CodeExecutor()
        code = """
public class Solution {
    public static void main(String[] args) {
        System.out.println("Hello, World!");
    }
}
"""
        try:
            result = executor.execute(code, 'java')
            assert result['output'] == "Hello, World!"
        finally:
            executor.cleanup()
    
    @pytest.mark.skipif(True, reason="Requires javac and java installed")
    def test_java_compilation_error(self):
        """Test Java compilation error"""
        executor = CodeExecutor()
        code = """
public class Solution {
    public static void main(String[] args) {
        System.out.println("Missing semicolon")
    }
}
"""
        with pytest.raises(CodeExecutionError, match="Compilation Error"):
            executor.execute(code, 'java')
        executor.cleanup()


class TestCodeExecutor:
    """General tests for CodeExecutor"""
    
    def test_unsupported_language(self):
        """Test unsupported language error"""
        executor = CodeExecutor()
        with pytest.raises(ValueError, match="Unsupported language"):
            executor.execute("code", "ruby")
        executor.cleanup()
    
    def test_cleanup(self):
        """Test cleanup removes temporary directory"""
        import os
        executor = CodeExecutor()
        temp_dir = executor.temp_dir
        assert os.path.exists(temp_dir)
        
        executor.cleanup()
        assert not os.path.exists(temp_dir)
    
    def test_multiple_executions(self):
        """Test multiple code executions"""
        executor = CodeExecutor()
        code1 = 'print("First")'
        code2 = 'print("Second")'
        
        try:
            result1 = executor.execute(code1, 'python')
            result2 = executor.execute(code2, 'python')
            
            assert result1['output'] == "First"
            assert result2['output'] == "Second"
        finally:
            executor.cleanup()


class TestProblemSolutions:
    """Test complete problem solutions"""
    
    def test_two_sum_solution(self):
        """Test Two Sum problem solution"""
        executor = CodeExecutor()
        code = """
import json

def twoSum(nums, target):
    seen = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []

nums = json.loads(input())
target = int(input())
result = twoSum(nums, target)
print(json.dumps(result))
"""
        try:
            result = executor.execute(code, 'python', stdin_data="[2,7,11,15]\n9")
            assert "[0" in result['output'] and "1]" in result['output']
        finally:
            executor.cleanup()
    
    def test_reverse_string_solution(self):
        """Test Reverse String problem solution"""
        executor = CodeExecutor()
        code = """
import json

def reverseString(s):
    left, right = 0, len(s) - 1
    while left < right:
        s[left], s[right] = s[right], s[left]
        left += 1
        right -= 1

s = json.loads(input())
reverseString(s)
print(json.dumps(s))
"""
        try:
            result = executor.execute(code, 'python', stdin_data='["h","e","l","l","o"]')
            assert "o" in result['output']
        finally:
            executor.cleanup()


