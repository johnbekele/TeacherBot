"""
Subprocess-based sandbox for secure code execution
A lightweight alternative to Docker sandbox for development/testing
"""
import subprocess
import tempfile
import os
import time
import signal
from typing import Dict
from app.config import get_settings

settings = get_settings()


class SubprocessSandbox:
    """Manages subprocess-based code execution with security limits"""

    def __init__(self):
        print("✅ Subprocess sandbox initialized")

    def execute_code(
        self,
        code: str,
        language: str,
        timeout: int = None
    ) -> Dict[str, any]:
        """
        Execute code in subprocess with security limits

        Args:
            code: Code to execute
            language: Language (python, bash)
            timeout: Execution timeout in seconds

        Returns:
            Dict with stdout, stderr, exit_code, execution_time
        """
        timeout = timeout or settings.SANDBOX_TIMEOUT

        if language == "python":
            return self._execute_python(code, timeout)
        elif language == "bash":
            return self._execute_bash(code, timeout)
        else:
            return {
                "stdout": "",
                "stderr": f"Unsupported language: {language}",
                "exit_code": 1,
                "execution_time": 0
            }

    def _execute_python(self, code: str, timeout: int) -> Dict:
        """Execute Python code"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_file = f.name

        try:
            start_time = time.time()

            # Run Python with restricted environment
            result = subprocess.run(
                ['python3', temp_file],
                capture_output=True,
                timeout=timeout,
                text=True,
                env=self._get_restricted_env(),
                # Prevent shell injection
                shell=False
            )

            execution_time = time.time() - start_time

            # Truncate output if too large
            stdout = result.stdout
            stderr = result.stderr

            if len(stdout) > settings.MAX_OUTPUT_SIZE:
                stdout = stdout[:settings.MAX_OUTPUT_SIZE] + "\n... (output truncated)"
            if len(stderr) > settings.MAX_OUTPUT_SIZE:
                stderr = stderr[:settings.MAX_OUTPUT_SIZE] + "\n... (output truncated)"

            return {
                "stdout": stdout,
                "stderr": stderr,
                "exit_code": result.returncode,
                "execution_time": execution_time
            }

        except subprocess.TimeoutExpired:
            return {
                "stdout": "",
                "stderr": f"Execution timed out after {timeout} seconds",
                "exit_code": 124,  # Standard timeout exit code
                "execution_time": timeout
            }
        except Exception as e:
            return {
                "stdout": "",
                "stderr": f"Execution error: {str(e)}",
                "exit_code": 1,
                "execution_time": 0
            }
        finally:
            # Clean up temp file
            try:
                os.unlink(temp_file)
            except:
                pass

    def _execute_bash(self, code: str, timeout: int) -> Dict:
        """Execute Bash script"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
            f.write(code)
            temp_file = f.name

        # Make script executable
        os.chmod(temp_file, 0o755)

        try:
            start_time = time.time()

            # Run Bash with restricted environment
            result = subprocess.run(
                ['bash', temp_file],
                capture_output=True,
                timeout=timeout,
                text=True,
                env=self._get_restricted_env(),
                shell=False
            )

            execution_time = time.time() - start_time

            # Truncate output if too large
            stdout = result.stdout
            stderr = result.stderr

            if len(stdout) > settings.MAX_OUTPUT_SIZE:
                stdout = stdout[:settings.MAX_OUTPUT_SIZE] + "\n... (output truncated)"
            if len(stderr) > settings.MAX_OUTPUT_SIZE:
                stderr = stderr[:settings.MAX_OUTPUT_SIZE] + "\n... (output truncated)"

            return {
                "stdout": stdout,
                "stderr": stderr,
                "exit_code": result.returncode,
                "execution_time": execution_time
            }

        except subprocess.TimeoutExpired:
            return {
                "stdout": "",
                "stderr": f"Execution timed out after {timeout} seconds",
                "exit_code": 124,
                "execution_time": timeout
            }
        except Exception as e:
            return {
                "stdout": "",
                "stderr": f"Execution error: {str(e)}",
                "exit_code": 1,
                "execution_time": 0
            }
        finally:
            # Clean up temp file
            try:
                os.unlink(temp_file)
            except:
                pass

    def _get_restricted_env(self) -> Dict[str, str]:
        """Get restricted environment variables"""
        # Minimal safe environment
        return {
            'PATH': '/usr/local/bin:/usr/bin:/bin',
            'LANG': 'C.UTF-8',
            'LC_ALL': 'C.UTF-8',
            # Prevent network access hints
            'http_proxy': 'http://127.0.0.1:1',
            'https_proxy': 'http://127.0.0.1:1',
        }


# Singleton instance
sandbox = SubprocessSandbox()
