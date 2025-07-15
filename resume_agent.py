from transformers import pipeline
import torch

# Force CPU device
device = -1  # -1 means CPU for Hugging Face pipelines

# Load LLM pipeline for text-generation on CPU
qa_pipeline = pipeline("text-generation", model="distilgpt2", device=-1)


def get_improvement_suggestions(section_name, section_text):
    prompt = f"""
You are an expert Resume Reviewer AI. Analyze the following {section_name} section of a resume.

Section Content:
{section_text}

1. Cross-question to check clarity, impact, and relevance. Ask direct questions to improve it.
2. Provide actionable improvement suggestions in bullet points.

Format:
Questions:
-
Suggestions:
-
    """
    # Set max_new_tokens instead of max_length to avoid warning
    response = qa_pipeline(prompt, max_new_tokens=512, do_sample=False)
    return response[0]['generated_text']


# Example usage
if __name__ == "__main__":
    example_section = "Led a team of 5 engineers to build a scalable data pipeline for real-time analytics."
    print(get_improvement_suggestions("experience", example_section))
