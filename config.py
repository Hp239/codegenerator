import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Project Information
PROJECT_NAME = "CodeGeneratorAI"
VERSION = "1.0"

# Gemini Configuration

# Read API key from .env
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

MODEL_NAME = "gemini-2.5-flash"

MAX_NEW_TOKENS = 1024
TEMPERATURE = 0.7

# File Configuration


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

OUTPUT_FOLDER = os.path.join(BASE_DIR, "outputs")

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

OUTPUT_FILE = os.path.join(
    OUTPUT_FOLDER,
    "generated_code.py"
)

PAGE_TITLE = "AI Code Generator"

PAGE_ICON = "🤖"

LAYOUT = "wide"

SUPPORTED_LANGUAGES = [
    "Python",
    "Java",
    "C",
    "C++",
    "JavaScript",
    "HTML",
    "CSS"
]

if __name__ == "__main__":

    print("=" * 40)
    print("Project :", PROJECT_NAME)
    print("Version :", VERSION)
    print("Model :", MODEL_NAME)
    print("API Loaded :", bool(GEMINI_API_KEY))
    print("=" * 40)