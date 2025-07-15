import streamlit as st
import pdfplumber
import requests
import time
import re

# Hugging Face API details
HF_API_URL = "https://api-inference.huggingface.co/models/tiiuae/falcon-7b-instruct"

HF_API_TOKEN = "hf_XXXXXXXXXXXXXXXXXXXXXXXXXX" # Replace with your actual token

headers = {
    "Authorization": f"Bearer {HF_API_TOKEN}",
    "Content-Type": "application/json",
}

def extract_text_from_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

def split_into_sections(text):
    sections = {}
    keywords = ["summary", "experience", "skills", "projects", "education"]
    current_section = None
    lines = text.lower().splitlines()
    buffer = []
    for line in lines:
        line_stripped = line.strip()
        if line_stripped in keywords:
            if current_section and buffer:
                sections[current_section] = "\n".join(buffer).strip()
                buffer = []
            current_section = line_stripped
        elif current_section:
            buffer.append(line)
    if current_section and buffer:
        sections[current_section] = "\n".join(buffer).strip()
    return sections

def get_improvement_suggestions(section_name, section_text, retries=3):
    prompt = f"""
You are an expert resume reviewer.

Your task is to analyze the following {section_name} section of a resume and provide:

1. Two direct, thoughtful questions to ask the candidate to improve this section.
2. Three actionable improvement suggestions written as complete sentences starting with a strong verb.

Return the output in the following format:

Questions:
- [First question]
- [Second question]

Suggestions:
- [First actionable improvement suggestion]
- [Second actionable improvement suggestion]
- [Third actionable improvement suggestion]

Section:
{section_text}
"""
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 512,
            "temperature": 0.7,
            "top_p": 1,
        },
    }
    for attempt in range(retries):
        try:
            response = requests.post(HF_API_URL, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            if isinstance(data, list) and "generated_text" in data[0]:
                return data[0]["generated_text"].strip()
            else:
                return "Unexpected response format from Hugging Face API."
        except requests.exceptions.HTTPError as e:
            if response.status_code == 503:
                st.warning("Model is loading, waiting a few seconds...")
                time.sleep(5)
                continue
            return f"HTTP error: {str(e)}"
        except Exception as e:
            return f"Error calling Hugging Face API: {str(e)}"
    return "Failed to get response from Hugging Face API after multiple attempts."

def clean_and_format_list(text):
    lines = re.split(r"\n|- ", text)
    items = [line.strip().capitalize() for line in lines if line.strip()]
    formatted = []
    for item in items:
        if not item.endswith("."):
            item += "."
        formatted.append(item)
    return formatted

# -------------------- Streamlit UI --------------------
st.set_page_config(page_title="🤖 AI Resume Chatbot Coach", layout="wide")
st.title("🤖 AI Resume Chatbot Coach with Hugging Face API")

if "stage" not in st.session_state:
    st.session_state.stage = "start"
if "sections" not in st.session_state:
    st.session_state.sections = {}

if st.session_state.stage == "start":
    st.write("👋 Hello! I am your AI Resume Reviewer powered by Hugging Face. Are you looking to improve your resume today?")
    user_input = st.text_input("Type 'yes' to continue.")
    if user_input.lower() == "yes":
        st.session_state.stage = "upload"
        st.rerun()

elif st.session_state.stage == "upload":
    uploaded_file = st.file_uploader("📄 Upload your resume (PDF)", type="pdf")
    if uploaded_file:
        with st.spinner("Extracting text from PDF..."):
            full_text = extract_text_from_pdf(uploaded_file)
            st.session_state.sections = split_into_sections(full_text)
        st.success("✅ Resume uploaded and sections extracted!")
        st.session_state.stage = "select_section"
        st.rerun()

elif st.session_state.stage == "select_section":
    sections = st.session_state.sections
    if not sections:
        st.warning("No recognizable sections found. Ensure your resume includes headers like Summary, Experience, Skills, Projects, Education.")
    else:
        st.write("💡 Which section would you like to improve?")
        section_options = list(sections.keys())
        selected_section = st.selectbox("Select a section", section_options)
        if st.button("Review this section"):
            st.session_state.selected_section = selected_section
            st.session_state.stage = "show_suggestions"
            st.rerun()

elif st.session_state.stage == "show_suggestions":
    section_name = st.session_state.selected_section
    section_text = st.session_state.sections[section_name]
    st.write(f"📄 **{section_name.title()} Section Content:**")
    st.write(section_text)
    with st.spinner("✨ Generating improvement suggestions..."):
        suggestions_raw = get_improvement_suggestions(section_name, section_text)
    st.subheader("✅ Improvement Suggestions")
    if "Questions:" in suggestions_raw and "Suggestions:" in suggestions_raw:
        parts = suggestions_raw.split("Suggestions:")
        questions_part = parts[0].replace("Questions:", "").strip()
        suggestions_part = parts[1].strip()
        st.markdown("**❓ Questions to Reflect On:**")
        questions = clean_and_format_list(questions_part)
        for q in questions:
            st.markdown(f"- {q}")
        st.markdown("**💡 Expert Suggestions for Improvement:**")
        suggestions = clean_and_format_list(suggestions_part)
        for s in suggestions:
            st.markdown(f"- {s}")
    else:
        st.markdown(suggestions_raw)
    st.write("💬 Would you like to improve another section?")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Yes, choose another section"):
            st.session_state.stage = "select_section"
            st.rerun()
    with col2:
        if st.button("Exit"):
            st.session_state.stage = "exit"
            st.rerun()

elif st.session_state.stage == "exit":
    st.write("🎉 Thank you for using the AI Resume Chatbot Coach!")
    if st.button("Restart"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
