"""
=========================================
CodeGeneratorAI - Code Generator
=========================================
"""

from model import AIModel


SUPPORTED_LANGUAGES = [
    "Python",
    "Java",
    "C",
    "C++",
    "JavaScript",
    "HTML",
    "CSS"
]


def generate_prompt(language, user_request):

    if language not in SUPPORTED_LANGUAGES:
        return "Unsupported Programming Language."

    prompt = f"""
You are a code generator.

Programming Language:
{language}

User Requirement:
{user_request}

IMPORTANT:
Your response MUST contain ONLY the final source code.

DO NOT:
- explain anything
- describe the solution
- write "The user wants..."
- write "Constraints check"
- write "# THINK"
- write analysis
- write markdown
- use ``` code blocks
- write documentation
- write comments
- write sample output
- write expected output
- write test cases


Return ONLY valid {language} source code.

The first character of your response must be part of the source code.

The last character of your response must be part of the source code.

Generate simple, beginner-friendly and executable code.
Use the shortest correct solution.
Do not add unnecessary functions or classes.
Do not add unnecessary imports.
Do not use type hints unless required.

JAVASCRIPT INPUT RULE:
If the task requires user input in JavaScript, do NOT use prompt() or browser functions.
Instead use this exact pattern to read input from stdin in Node.js:

const data = require('fs').readFileSync('/dev/stdin', 'utf-8').trim();
const num = parseInt(data);

Use readFileSync('/dev/stdin', 'utf-8') only once at the top of the program
if multiple values are needed, split the data by newline or space.
"""

    return prompt


def clean_generated_code(code, language):

    if not code:
        return ""

    code = code.strip()

    # Remove markdown code blocks if Gemini adds them
    if code.startswith("```"):

        lines = code.splitlines()

        if lines:
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        code = "\n".join(lines).strip()

    # Remove accidental closing code fence
    code = code.replace("```", "").strip()

    # Remove common Gemini analysis prefixes
    unwanted_prefixes = [
        "# THINK",
        "THINK:",
        "Analysis:",
        "analysis:",
        "Here is the code:",
        "Here is the Python code:",
        "Here is the Java code:",
        "Here is the C code:",
        "Here is the C++ code:",
        "Here is the JavaScript code:",
    ]

    for prefix in unwanted_prefixes:

        if code.startswith(prefix):

            code = code[len(prefix):].strip()

    return code


def generate_code(language, user_request):

    prompt = generate_prompt(
        language,
        user_request
    )

    ai = AIModel()

    generated_code = ai.generate_code(prompt)

    generated_code = clean_generated_code(
        generated_code,
        language
    )

    return generated_code


# =========================================
# Testing
# =========================================

if __name__ == "__main__":

    language = input(
        "Select Language : "
    )

    user_request = input(
        "Enter Requirement : "
    )

    code = generate_code(
        language,
        user_request
    )

    print("\nGenerated Code:\n")

    print(code)