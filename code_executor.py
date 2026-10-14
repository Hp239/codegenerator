"""
=========================================
CodeGeneratorAI - Code Executor
Uses JDoodle Compiler API for running code
=========================================
"""

import requests


JDOODLE_URL = "https://api.jdoodle.com/v1/execute"

# ============================================
# PUT YOUR OWN JDOODLE CREDENTIALS HERE
# ============================================
CLIENT_ID ="875c68c5be5221ee5af5cc8a8a1a238"
CLIENT_SECRET = "2ac4d7e2baad1114e386dd26e56aa89318f4a3471d15a10a946f819fb8c43755"


# JDoodle language codes
LANGUAGE_MAP = {
    "Python": {"language": "python3", "versionIndex": "4"},
    "Java": {"language": "java", "versionIndex": "4"},
    "C": {"language": "c", "versionIndex": "5"},
    "C++": {"language": "cpp17", "versionIndex": "1"},
    "JavaScript": {"language": "nodejs", "versionIndex": "4"},
}


class CodeExecutor:

    def run_code(self, language, code, stdin=""):
        """
        Run any supported code using the JDoodle API.

        Parameters:
            language (str): Programming language
            code (str): Source code to run
            stdin (str): Optional input for the program

        Returns:
            dict
        """

        if language not in LANGUAGE_MAP:
            return {
                "success": False,
                "output": f"{language} execution is not supported."
            }

        lang_info = LANGUAGE_MAP[language]

        payload = {
            "clientId": CLIENT_ID,
            "clientSecret": CLIENT_SECRET,
            "script": code,
            "language": lang_info["language"],
            "versionIndex": lang_info["versionIndex"],
            "stdin": stdin
        }

        try:

            response = requests.post(
                JDOODLE_URL,
                json=payload,
                timeout=30
            )

            if response.status_code != 200:
                return {
                    "success": False,
                    "output": f"JDoodle error: HTTP {response.status_code} - {response.text}"
                }

            result = response.json()

            # JDoodle returns a non-empty "error" key only when something actually fails
            if result.get("error"):
                return {
                    "success": False,
                    "output": f"JDoodle Error: {result['error']}"
                }

            output = result.get("output", "")
            status_code = result.get("statusCode", 200)

            if status_code != 200:
                return {
                    "success": False,
                    "output": output if output else "Execution failed."
                }

            return {
                "success": True,
                "output": output if output else "(No output)"
            }

        except requests.exceptions.ConnectionError:
            return {
                "success": False,
                "output": "Could not connect to JDoodle API. Check your internet connection."
            }

        except Exception as e:
            return {
                "success": False,
                "output": f"Unexpected error: {str(e)}"
            }


if __name__ == "__main__":

    executor = CodeExecutor()

    lang = input("Language: ")
    print("Enter code (end with an empty line):")

    lines = []
    while True:
        line = input()
        if line == "":
            break
        lines.append(line)

    source = "\n".join(lines)

    result = executor.run_code(lang, source)

    print("\n--- OUTPUT ---")
    print(result["output"])
