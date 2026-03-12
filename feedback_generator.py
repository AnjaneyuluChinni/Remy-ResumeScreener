import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

GEMINI_PROMPT_TEMPLATE = """
You are an ATS resume evaluator.

Analyze the resume against the job description.

Return STRICTLY in this format:

ATS Match Score: <number>%

Missing Skills:
- skill 1
- skill 2

Suggestions:
- suggestion 1
- suggestion 2
- suggestion 3

Feedback Summary:
<short paragraph>

Resume:
{resume_text}

Job Description:
{jd_text}
"""

def generate_feedback(resume_text, jd_text, gemini_api_key=None):
    """
    Generate resume feedback using Google Gemini (gemini-pro).
    Returns a dict with score, missing_skills, suggestions, summary, and raw_response.
    """
    if gemini_api_key is None:
        gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        raise ValueError("Gemini API key not set. Set GEMINI_API_KEY in your .env or environment.")

    genai.configure(api_key=gemini_api_key)
    prompt = GEMINI_PROMPT_TEMPLATE.format(resume_text=resume_text, jd_text=jd_text)
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        text = response.text.strip()
        # Parse the response into structured feedback
        feedback = parse_gemini_feedback(text)
        feedback['raw_response'] = text
        return feedback
    except Exception as e:
        return {"error": str(e)}

def parse_gemini_feedback(text):
    import re

    feedback = {
        "score": None,
        "missing_skills": [],
        "suggestions": [],
        "summary": ""
    }

    # ATS Score
    score_match = re.search(r'(\d+)%', text)
    if score_match:
        feedback["score"] = int(score_match.group(1))

    # Missing skills
    missing_section = re.search(
        r"(Missing.*?:)([\s\S]*?)(Suggestions|Feedback)",
        text,
        re.IGNORECASE
    )

    if missing_section:
        feedback["missing_skills"] = [
            line.strip("-• ").strip()
            for line in missing_section.group(2).split("\n")
            if line.strip()
        ]

    # Suggestions
    suggestion_section = re.search(
        r"(Suggestions.*?:)([\s\S]*?)(Feedback|$)",
        text,
        re.IGNORECASE
    )

    if suggestion_section:
        feedback["suggestions"] = [
            line.strip("-• ").strip()
            for line in suggestion_section.group(2).split("\n")
            if line.strip()
        ]

    # Summary
    summary_section = re.search(
        r"(Feedback.*?:)([\s\S]*)",
        text,
        re.IGNORECASE
    )

    if summary_section:
        feedback["summary"] = summary_section.group(2).strip()

    return feedback

feedback = parse_gemini_feedback(text)

# Fallback suggestions if parsing fails
if not feedback["suggestions"]:
    feedback["suggestions"] = [
        "Add measurable achievements in your project descriptions",
        "Include more keywords from the job description",
        "Strengthen your professional summary with role-specific skills"
    ]

feedback['raw_response'] = text
return feedback
