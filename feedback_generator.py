import os
import re
import streamlit as st
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
    Generate resume feedback using Google Gemini.
    Returns a dict with score, missing_skills, suggestions, summary, and raw_response.
    """

    # Get API key (local .env OR Streamlit secrets)
    if gemini_api_key is None:
        gemini_api_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")

    if not gemini_api_key:
        raise ValueError(
            "Gemini API key not set. Add GEMINI_API_KEY to .env or Streamlit secrets."
        )

    genai.configure(api_key=gemini_api_key)

    # Limit prompt size (prevents Gemini token errors)
    resume_text = resume_text[:8000]
    jd_text = jd_text[:8000]

    prompt = GEMINI_PROMPT_TEMPLATE.format(
        resume_text=resume_text,
        jd_text=jd_text
    )

    try:
        model = genai.GenerativeModel("gemini-pro")

        response = model.generate_content(prompt)

        if not response or not hasattr(response, "text"):
            return {
                "score": None,
                "missing_skills": [],
                "suggestions": [
                    "AI feedback could not be generated. Please try again."
                ],
                "summary": "",
                "raw_response": ""
            }

        text = response.text.strip()

        feedback = parse_gemini_feedback(text)

        # Fallback suggestions
        if not feedback["suggestions"]:
            feedback["suggestions"] = [
                "Add measurable achievements in your project descriptions",
                "Include more keywords from the job description",
                "Strengthen your professional summary with role-specific skills"
            ]

        feedback["raw_response"] = text

        return feedback

    except Exception as e:
        print("GEMINI ERROR:", e)

        return {
            "score": None,
            "missing_skills": [],
            "suggestions": [
                f"AI feedback generation failed: {str(e)}"
            ],
            "summary": ""
        }


def parse_gemini_feedback(text):
    """
    Parse Gemini structured response into a dictionary.
    """

    feedback = {
        "score": None,
        "missing_skills": [],
        "suggestions": [],
        "summary": ""
    }

    # ATS score
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
