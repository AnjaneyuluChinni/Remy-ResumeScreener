import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

GEMINI_PROMPT_TEMPLATE = """
You are a professional AI assistant that helps job seekers improve their resumes.

Resume:
------------------
{resume_text}

Job Description:
------------------
{jd_text}

Analyze the resume in the context of the job description and provide:
1. ATS match score (0%–100%)
2. Missing keywords or skills
3. Suggestions for improving the resume
4. A professional feedback summary

Format:
**ATS Match Score:** XX%

**Missing Skills/Keywords:**
- item 1
- item 2

**Suggestions to Improve Resume:**
- Suggestion 1
- Suggestion 2

**Feedback Summary:**
<summary here>
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
        model = genai.GenerativeModel("models/gemini-2.0-flash")
        response = model.generate_content(prompt)
        text = response.text.strip()
        # Parse the response into structured feedback
        feedback = parse_gemini_feedback(text)
        feedback['raw_response'] = text
        return feedback
    except Exception as e:
        return {"error": str(e)}

def parse_gemini_feedback(text):
    """
    Parse Gemini's structured feedback into a dict.
    """
    import re
    feedback = {}
    # ATS Match Score
    score_match = re.search(r"\*\*ATS Match Score:\*\*\s*(\d+)%", text)
    feedback['score'] = int(score_match.group(1)) if score_match else None
    # Missing Skills/Keywords
    missing = re.findall(r"\*\*Missing Skills/Keywords:\*\*[\s\-]*([\s\S]*?)\n\*\*Suggestions to Improve Resume:\*\*", text)
    if missing:
        feedback['missing_skills'] = [line.strip('- ').strip() for line in missing[0].split('\n') if line.strip('- ').strip()]
    else:
        feedback['missing_skills'] = []
    # Suggestions
    suggestions = re.findall(r"\*\*Suggestions to Improve Resume:\*\*[\s\-]*([\s\S]*?)\n\*\*Feedback Summary:\*\*", text)
    if suggestions:
        feedback['suggestions'] = [line.strip('- ').strip() for line in suggestions[0].split('\n') if line.strip('- ').strip()]
    else:
        feedback['suggestions'] = []
    # Feedback Summary
    summary_match = re.search(r"\*\*Feedback Summary:\*\*\s*([\s\S]*)", text)
    feedback['summary'] = summary_match.group(1).strip() if summary_match else ""
    return feedback 