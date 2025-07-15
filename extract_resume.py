import pdfplumber
import re


def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

# Example usage:
# resume_text = extract_text_from_pdf("/Users/aditi/Documents/resume_agent/Aditi_Mishra_Res.pdf")
# print(resume_text)


