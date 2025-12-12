import PyPDF2
from typing import Optional

class DocumentProcessor:
    @staticmethod
    def extract_text(uploaded_file) -> str:
        if uploaded_file.type == "application/pdf":
            reader = PyPDF2.PdfReader(uploaded_file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
        else:
            # Assuming text file
            return uploaded_file.getvalue().decode("utf-8")