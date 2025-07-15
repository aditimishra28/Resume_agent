from extract_resume import extract_text_from_pdf
from parse_resume import parse_resume_sections
from resume_agent import get_improvement_suggestions

if __name__ == "__main__":
    pdf_path = "Aditi_Mishra_Res.pdf"
    resume_text = extract_text_from_pdf(pdf_path)
    parsed_sections = parse_resume_sections(resume_text)

    for section, content in parsed_sections.items():
        print(f"\n--- {section.upper()} ---\n")
        suggestions = get_improvement_suggestions(section, content)
        print(suggestions)
