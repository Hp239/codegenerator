"""
--------------- Backend -----------------------

This file connects:
1. Prompt Generator
2. AI Model
3. File Handler
4. Code Executor
"""

from code_generator import generate_code
from file_handler import FileHandler
from code_executor import CodeExecutor


class Backend:

    def __init__(self):
        """
        Initialize File Handler
        and Code Executor.
        """

        self.file_handler = FileHandler()
        self.code_executor = CodeExecutor()

    def generate(self, language, user_request):
        """
        Generate code and save it.

        Parameters:
            language (str): Programming language
            user_request (str): User prompt

        Returns:
            dict
        """

        try:

            # Generate code using AI
            generated_code = generate_code(
                language,
                user_request
            )

            # Save generated code
            file_path = self.file_handler.save_code(
                generated_code,
                language
            )

            return {
                "success": True,
                "code": generated_code,
                "file_path": file_path
            }

        except Exception as e:

            return {
                "success": False,
                "error": str(e)
            }

    def run_code(self, language, code, stdin=""):
        """
        Run generated code.

        Currently Python execution is supported.

        Parameters:
            language (str): Programming language
            code (str): Generated code

        Returns:
            dict
        """
        try:

            return self.code_executor.run_code(language, code, stdin)

        except Exception as e:

            return {
                "success": False,
                "output": str(e)
            }

if __name__ == "__main__":

    backend = Backend()

    language = input(
        "Programming Language : "
    )

    user_request = input(
        "Enter Requirement : "
    )

    # Generate code
    result = backend.generate(
        language,
        user_request
    )

    if result["success"]:

        print(
            "\n========== GENERATED CODE ==========\n"
        )

        print(result["code"])

        print(
            "\n===================================="
        )

        print("\nFile Saved At:")
        print(result["file_path"])

        # Run generated code
        if language == "Python":

            run_result = backend.run_code(
                language,
                result["code"]
            )

            print(
                "\n========== PROGRAM OUTPUT ==========\n"
            )

            if run_result["success"]:
                print(run_result["output"])
            else:
                print(run_result["output"])

            print(
                "\n===================================="
            )

    else:

        print("\nError:")
        print(result["error"])