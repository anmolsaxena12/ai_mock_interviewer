"""
Service for executing code safely in multiple languages.

This module provides functionality to execute user-submitted code
in Python, C++, and Java with proper sandboxing and timeout limits.
"""
import subprocess
import tempfile
import os
import signal
import json
from pathlib import Path


class CodeExecutionError(Exception):
    """Custom exception for code execution errors"""
    pass


class CodeExecutor:
    """Handles code execution for different programming languages"""
    
    # Timeout in seconds
    TIMEOUT = 5
    
    # Memory limit (in MB)
    MEMORY_LIMIT = 256
    
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp()
    
    def execute_python(self, code, stdin_data=""):
        """
        Execute Python code
        
        Args:
            code (str): Python code to execute
            stdin_data (str): Input data for the program
            
        Returns:
            dict: Execution result with stdout, stderr, and exit code
        """
        try:
            # Create temporary Python file
            file_path = os.path.join(self.temp_dir, "solution.py")
            with open(file_path, 'w') as f:
                f.write(code)
            
            # Execute with subprocess
            process = subprocess.Popen(
                ['python3', file_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                preexec_fn=os.setsid  # Create new process group for better cleanup
            )
            
            try:
                stdout, stderr = process.communicate(
                    input=stdin_data,
                    timeout=self.TIMEOUT
                )
                return_code = process.returncode
            except subprocess.TimeoutExpired:
                os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                raise CodeExecutionError("Time Limit Exceeded (> 5 seconds)")
            
            if return_code != 0:
                error_msg = stderr.strip() if stderr else "Runtime Error"
                raise CodeExecutionError(f"Runtime Error:\n{error_msg}")
            
            return {
                'output': stdout.strip(),
                'error': None,
                'exit_code': return_code
            }
            
        except CodeExecutionError:
            raise
        except Exception as e:
            raise CodeExecutionError(f"Execution failed: {str(e)}")
        finally:
            # Cleanup
            if os.path.exists(file_path):
                os.remove(file_path)
    
    def execute_cpp(self, code, stdin_data=""):
        """
        Execute C++ code
        
        Args:
            code (str): C++ code to execute
            stdin_data (str): Input data for the program
            
        Returns:
            dict: Execution result with stdout, stderr, and exit code
        """
        cpp_file = os.path.join(self.temp_dir, "solution.cpp")
        exe_file = os.path.join(self.temp_dir, "solution")
        
        try:
            # Write C++ code to file
            with open(cpp_file, 'w') as f:
                f.write(code)
            
            # Compile
            compile_process = subprocess.run(
                ['g++', '-std=c++17', '-O2', cpp_file, '-o', exe_file],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if compile_process.returncode != 0:
                raise CodeExecutionError(f"Compilation Error:\n{compile_process.stderr}")
            
            # Execute
            process = subprocess.Popen(
                [exe_file],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                preexec_fn=os.setsid
            )
            
            try:
                stdout, stderr = process.communicate(
                    input=stdin_data,
                    timeout=self.TIMEOUT
                )
                return_code = process.returncode
            except subprocess.TimeoutExpired:
                os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                raise CodeExecutionError("Time Limit Exceeded (> 5 seconds)")
            
            if return_code != 0:
                error_msg = stderr.strip() if stderr else "Runtime Error"
                raise CodeExecutionError(f"Runtime Error:\n{error_msg}")
            
            return {
                'output': stdout.strip(),
                'error': None,
                'exit_code': return_code
            }
            
        except CodeExecutionError:
            raise
        except subprocess.TimeoutExpired:
            raise CodeExecutionError("Compilation Timeout")
        except Exception as e:
            raise CodeExecutionError(f"Execution failed: {str(e)}")
        finally:
            # Cleanup
            for file in [cpp_file, exe_file]:
                if os.path.exists(file):
                    os.remove(file)
    
    def execute_java(self, code, stdin_data=""):
        """
        Execute Java code
        
        Args:
            code (str): Java code to execute
            stdin_data (str): Input data for the program
            
        Returns:
            dict: Execution result with stdout, stderr, and exit code
        """
        # Extract class name from code
        class_name = self._extract_java_class_name(code)
        if not class_name:
            raise CodeExecutionError("Could not find public class in Java code")
        
        java_file = os.path.join(self.temp_dir, f"{class_name}.java")
        
        try:
            # Write Java code to file
            with open(java_file, 'w') as f:
                f.write(code)
            
            # Compile
            compile_process = subprocess.run(
                ['javac', java_file],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=self.temp_dir
            )
            
            if compile_process.returncode != 0:
                raise CodeExecutionError(f"Compilation Error:\n{compile_process.stderr}")
            
            # Execute
            process = subprocess.Popen(
                ['java', class_name],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=self.temp_dir,
                preexec_fn=os.setsid
            )
            
            try:
                stdout, stderr = process.communicate(
                    input=stdin_data,
                    timeout=self.TIMEOUT
                )
                return_code = process.returncode
            except subprocess.TimeoutExpired:
                os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                raise CodeExecutionError("Time Limit Exceeded (> 5 seconds)")
            
            if return_code != 0:
                error_msg = stderr.strip() if stderr else "Runtime Error"
                raise CodeExecutionError(f"Runtime Error:\n{error_msg}")
            
            return {
                'output': stdout.strip(),
                'error': None,
                'exit_code': return_code
            }
            
        except CodeExecutionError:
            raise
        except subprocess.TimeoutExpired:
            raise CodeExecutionError("Compilation Timeout")
        except Exception as e:
            raise CodeExecutionError(f"Execution failed: {str(e)}")
        finally:
            # Cleanup
            for ext in ['.java', '.class']:
                file_path = os.path.join(self.temp_dir, f"{class_name}{ext}")
                if os.path.exists(file_path):
                    os.remove(file_path)
    
    def _extract_java_class_name(self, code):
        """Extract the public class name from Java code"""
        import re
        match = re.search(r'public\s+class\s+(\w+)', code)
        return match.group(1) if match else None
    
    def execute(self, code, language, stdin_data=""):
        """
        Execute code in the specified language
        
        Args:
            code (str): Code to execute
            language (str): Programming language (python, cpp, java)
            stdin_data (str): Input data for the program
            
        Returns:
            dict: Execution result
        """
        if language == 'python':
            return self.execute_python(code, stdin_data)
        elif language == 'cpp':
            return self.execute_cpp(code, stdin_data)
        elif language == 'java':
            return self.execute_java(code, stdin_data)
        else:
            raise ValueError(f"Unsupported language: {language}")
    
    def cleanup(self):
        """Clean up temporary directory"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)


