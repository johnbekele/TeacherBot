"""
Docker-based sandbox for secure code execution
"""
import docker
import tempfile
import os
import time
from typing import Dict, Tuple
from app.config import get_settings

settings = get_settings()


class DockerSandbox:
    """Manages Docker-based code execution"""

    def __init__(self):
        try:
            self.client = docker.from_env()
            # Test connection
            self.client.ping()
            print("✅ Docker client connected")
        except Exception as e:
            print(f"⚠️  Docker client initialization failed: {e}")
            self.client = None

    def execute_code(
        self,
        code: str,
        language: str,
        timeout: int = None
    ) -> Dict[str, any]:
        """
        Execute code in isolated Docker container

        Args:
            code: Code to execute
            language: Language (python, bash)
            timeout: Execution timeout in seconds

        Returns:
            Dict with stdout, stderr, exit_code, execution_time
        """
        if not self.client:
            return {
                "stdout": "",
                "stderr": "Docker client not available",
                "exit_code": 1,
                "execution_time": 0
            }

        timeout = timeout or settings.SANDBOX_TIMEOUT

        # Select image based on language
        image_map = {
            "python": "myteacher-sandbox-python",
            "bash": "myteacher-sandbox-bash"
        }

        image = image_map.get(language)
        if not image:
            return {
                "stdout": "",
                "stderr": f"Unsupported language: {language}",
                "exit_code": 1,
                "execution_time": 0
            }

        # Create temporary directory for code
        with tempfile.TemporaryDirectory() as tmpdir:
            # Write code to file
            if language == "python":
                code_file = os.path.join(tmpdir, "main.py")
                command = ["python", "/workspace/main.py"]
            elif language == "bash":
                code_file = os.path.join(tmpdir, "script.sh")
                command = ["bash", "/workspace/script.sh"]

            with open(code_file, "w") as f:
                f.write(code)

            # Build image if it doesn't exist
            try:
                self.client.images.get(image)
            except docker.errors.ImageNotFound:
                self._build_image(language, image)

            # Execute in container
            try:
                start_time = time.time()

                container = self.client.containers.run(
                    image=image,
                    command=command,
                    volumes={tmpdir: {"bind": "/workspace", "mode": "ro"}},
                    network_mode="none",  # No network access
                    mem_limit=settings.SANDBOX_MEMORY_LIMIT,
                    cpu_quota=int(float(settings.SANDBOX_CPU_LIMIT) * 100000),
                    detach=True,
                    remove=True,
                    security_opt=["no-new-privileges"],
                    cap_drop=["ALL"]
                )

                # Wait for completion with timeout
                result = container.wait(timeout=timeout)
                execution_time = time.time() - start_time

                # Get logs
                logs = container.logs(stdout=True, stderr=True)
                output = logs.decode("utf-8")

                # Separate stdout and stderr (simplified)
                stdout = output
                stderr = ""
                exit_code = result["StatusCode"]

                # Truncate output if too large
                if len(stdout) > settings.MAX_OUTPUT_SIZE:
                    stdout = stdout[:settings.MAX_OUTPUT_SIZE] + "\n... (output truncated)"

                return {
                    "stdout": stdout,
                    "stderr": stderr,
                    "exit_code": exit_code,
                    "execution_time": execution_time
                }

            except docker.errors.ContainerError as e:
                return {
                    "stdout": e.stdout.decode("utf-8") if e.stdout else "",
                    "stderr": e.stderr.decode("utf-8") if e.stderr else str(e),
                    "exit_code": e.exit_status,
                    "execution_time": 0
                }
            except Exception as e:
                return {
                    "stdout": "",
                    "stderr": f"Execution error: {str(e)}",
                    "exit_code": 1,
                    "execution_time": 0
                }

    def _build_image(self, language: str, image_name: str):
        """Build sandbox Docker image"""
        try:
            dockerfile_path = f"./sandbox/{language}"
            print(f"🔨 Building {image_name}...")
            self.client.images.build(
                path=dockerfile_path,
                tag=image_name,
                rm=True
            )
            print(f"✅ Built {image_name}")
        except Exception as e:
            print(f"❌ Failed to build {image_name}: {e}")
            raise


# Singleton instance
sandbox = DockerSandbox()
