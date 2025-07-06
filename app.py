import streamlit as st
from resume_parser import extract_text
from feedback_generator import generate_feedback
import os
from dotenv import load_dotenv
from semantic_matcher import compute_semantic_similarity
import plotly.graph_objects as go
from ats_matcher import extract_keywords
from wordcloud import WordCloud
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import base64
import spacy

load_dotenv()

st.set_page_config(page_title="martResumeScan - AI Resume Screening", layout="wide")

st.markdown("""
<h1 style='text-align: center; color: #3F51B5;'>Remy</h1>
<h3 style='text-align: center; font-weight: 400; color: #5C6BC0;'>
Your AI-Powered Resume Coach
</h3>
<p style='text-align: center; color: #607D8B;'>
Upload your resume and job description — Remy will help you optimize your fit, highlight missing skills, and give smart, human-like feedback.
</p>
""", unsafe_allow_html=True)

# Sidebar with tips and FAQ
with st.sidebar:
    st.title("💡 Resume Tips & FAQ")
    st.markdown("""
- Use clear, concise language
- Tailor your resume to the job description
- Highlight relevant skills and achievements
- Use keywords from the JD
- Keep formatting clean and professional

**FAQ:**
- *What is a good similarity score?* 80%+ is excellent, 60–80% is good, below 60% needs improvement.
- *How are skills extracted?* Using NLP and AI models.
- *Is my data safe?* Yes, files are processed in-memory and not stored.
    """)



with st.form("upload_form"):
    col1, col2 = st.columns(2)
    with col1:
        resume_file = st.file_uploader("Upload Resume (PDF/DOCX)", type=["pdf", "docx", "doc"], key="resume")
    with col2:
        jd_file = st.file_uploader("Upload Job Description (PDF/DOCX)", type=["pdf", "docx", "doc"], key="jd")
    submitted = st.form_submit_button("Analyze")

if submitted:
    if not resume_file or not jd_file:
        st.error("Please upload both a resume and a job description.")
    else:
        with st.spinner("Extracting text from files..."):
            try:
                resume_text = extract_text(resume_file)
                jd_text = extract_text(jd_file)
            except Exception as e:
                st.error(f"Error extracting text: {e}")
                st.stop()

        st.success("Text extracted successfully!")

        # Compute semantic similarity score
        with st.spinner("Calculating semantic similarity score..."):
            semantic_score = compute_semantic_similarity(resume_text, jd_text)

        with st.spinner("Generating AI-powered suggestions and feedback..."):
            gemini_api_key = os.getenv("GEMINI_API_KEY")
            try:
                feedback = generate_feedback(resume_text, jd_text, gemini_api_key)
            except Exception as e:
                st.error(f"Error generating feedback: {e}")
                st.stop()

        # Extract skills for overlap chart and word cloud
        resume_skills = set(extract_keywords(resume_text))
        jd_skills = set(extract_keywords(jd_text))
        matched_skills = list(jd_skills & resume_skills)
        unmatched_skills = list(jd_skills - resume_skills)

        # Executive Summary Card
        def get_score_badge(score):
            if score >= 80:
                return "🟢 Excellent"
            elif score >= 60:
                return "🟠 Good"
            else:
                return "🔴 Needs Improvement"

        st.markdown("## Executive Summary")
        st.info(f"""
**Semantic Similarity Score:** {semantic_score}% {get_score_badge(semantic_score)}  
**Matched Skills:** {len(matched_skills)}  
**Unmatched Skills:** {len(unmatched_skills)}
""")
        if semantic_score >= 80:
            st.success("Your resume is a strong match for this job!")
        elif semantic_score >= 60:
            st.warning("Your resume is a decent match, but could be improved.")
        else:
            st.error("Your resume needs significant improvement to match this job.")

        # Colored Progress Bar
        def colored_progress(score):
            color = "#28a745" if score >= 80 else ("#ffc107" if score >= 60 else "#dc3545")
            st.markdown(f"""
<div style='height: 24px; background: {color}; width: {score}%; border-radius: 8px; text-align: center; color: white; font-weight: bold;'>
    {score}%
</div>
""", unsafe_allow_html=True)
        colored_progress(semantic_score)

        # Tabs for feedback
        tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Skills", "Suggestions", "Summary"])
        with tab1:
            st.markdown("### Overview")
            st.write("This section provides a high-level summary of your resume match.")
            st.write(f"Semantic Similarity Score: {semantic_score}%")
            st.write(f"Matched Skills: {len(matched_skills)}")
            st.write(f"Unmatched Skills: {len(unmatched_skills)}")
        with tab2:
            st.markdown("### Visual Skill Overlap Chart")
            skill_labels = ['Matched', 'Unmatched']
            skill_counts = [len(matched_skills), len(unmatched_skills)]
            fig = go.Figure(data=[go.Bar(x=skill_labels, y=skill_counts, marker_color=['green', 'red'])])
            fig.update_layout(title="Matched vs Unmatched Skills", yaxis_title="Count", xaxis_title="Skill Type")
            st.plotly_chart(fig, use_container_width=True)
            with st.expander("Show Matched Skills"):
                st.write(", ".join(matched_skills) if matched_skills else "None")
            with st.expander("Show Unmatched Skills"):
                st.write(", ".join(unmatched_skills) if unmatched_skills else "None")
            # Word Cloud
            st.markdown("#### Skill Word Cloud (JD)")
            if jd_skills:
                wc = WordCloud(width=600, height=300, background_color='white').generate(" ".join(jd_skills))
                buf = BytesIO()
                wc.to_image().save(buf, format='PNG')
                st.image(buf.getvalue(), use_column_width=True)
        with tab3:
            st.markdown("### Suggestions to Improve Resume:")
            suggestions = feedback.get('suggestions', [])
            if suggestions:
                for i, s in enumerate(suggestions, 1):
                    st.checkbox(f"{i}. {s}", value=False, key=f"suggestion_{i}")
            else:
                st.write("No suggestions provided.")
        with tab4:
            st.markdown("### Feedback Summary:")
            st.write(feedback.get('summary', ''))

        # Show extracted text with highlights
        with st.expander("Show Extracted Resume Text"):
            st.write(resume_text)
        with st.expander("Show Extracted JD Text"):
            st.write(jd_text)

        # Downloadable PDF Report
        def create_pdf_report():
            buf = BytesIO()
            c = canvas.Canvas(buf, pagesize=letter)
            c.setFont("Helvetica-Bold", 16)
            c.drawString(50, 750, "martResumeScan Resume Screening Report")
            c.setFont("Helvetica", 12)
            c.drawString(50, 720, f"Semantic Similarity Score: {semantic_score}%")
            c.drawString(50, 700, f"Matched Skills: {len(matched_skills)}")
            c.drawString(50, 680, f"Unmatched Skills: {len(unmatched_skills)}")
            c.drawString(50, 660, "Suggestions:")
            y = 640
            for s in feedback.get('suggestions', []):
                c.drawString(60, y, f"- {s}")
                y -= 20
            c.drawString(50, y, "Feedback Summary:")
            y -= 20
            for line in feedback.get('summary', '').split('\n'):
                c.drawString(60, y, line)
                y -= 20
            c.save()
            buf.seek(0)
            return buf
        pdf_buf = create_pdf_report()
        b64 = base64.b64encode(pdf_buf.read()).decode()
        st.download_button(
            label="Download PDF Report",
            data=base64.b64decode(b64),
            file_name="martResumeScan_Report.pdf",
            mime="application/pdf"
        )

        st.markdown("---")
        st.caption("martResumeScan | Powered by Streamlit, Gemini AI, Sentence Transformers, spaCy, and more.") 
