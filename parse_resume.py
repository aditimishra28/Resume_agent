import re

def parse_resume_sections(resume_text):
    sections = {}
    section_order = ["summary", "experience", "education", "skills", "projects"]
    section_patterns = {
        "summary": r"(Summary|Professional Summary|Profile)",
        "experience": r"(Experience|Work Experience|Professional Experience)",
        "education": r"(Education)",
        "skills": r"(Skills|Technical Skills)",
        "projects": r"(Projects)"
    }

    # Split by lines and find indices of headings
    lines = resume_text.splitlines()
    indices = {}
    for i, line in enumerate(lines):
        for sec, pattern in section_patterns.items():
            if re.search(pattern, line, re.IGNORECASE):
                indices[sec] = i

    # Sort indices by line number
    sorted_sections = sorted(indices.items(), key=lambda x: x[1])

    # Extract text between sections
    for idx, (sec, start_i) in enumerate(sorted_sections):
        end_i = sorted_sections[idx + 1][1] if idx + 1 < len(sorted_sections) else len(lines)
        sections[sec] = "\n".join(lines[start_i:end_i]).strip()

    return sections

# Example usage
# parsed = parse_resume_sections_v2(resume_text)
# print(parsed["experience"])
