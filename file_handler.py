"""
-------------File Handler--------------

This file is responsible for:
1. Creating output folder
2. Saving generated code
3. Reading generated code
"""

import os
from config import OUTPUT_FOLDER


class FileHandler:

    def __init__(self):
        """
        Create output folder if it doesn't exist.
        """
        os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    def get_extension(self, language):
        """
        Return file extension based on language.
        """

        extensions = {
            "Python": ".py",
            "Java": ".java",
            "C": ".c",
            "C++": ".cpp",
            "JavaScript": ".js",
            "HTML": ".html",
            "CSS": ".css"
        }

        return extensions.get(language, ".txt")

    def save_code(self, code, language):
        """
        Save generated code into outputs folder.
        """

        extension = self.get_extension(language)

        filename = "generated_code" + extension

        filepath = os.path.join(OUTPUT_FOLDER, filename)

        with open(filepath, "w", encoding="utf-8") as file:
            file.write(code)

        return filepath

    def read_code(self, filepath):
        """
        Read saved code file.
        """

        with open(filepath, "r", encoding="utf-8") as file:
            return file.read()




if __name__ == "__main__":

    handler = FileHandler()

    sample_code = """print("Hello World")"""

    path = handler.save_code(sample_code, "Python")

    print("File Saved Successfully!")

    print("Location:", path)

    print("\nFile Content:\n")

    print(handler.read_code(path))