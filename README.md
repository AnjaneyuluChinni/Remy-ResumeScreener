# Remy (martResumeScan)

Remy is an AI-powered resume screening and coaching application. Upload your resume and a job description, and Remy will:
- Analyze your fit using semantic similarity and Gemini AI
- Highlight missing and matched skills
- Suggest improvements
- Provide a professional feedback summary
- Visualize skill overlap and importance
- Let you download a PDF report

## Features
- **Gemini AI Feedback:** Personalized, actionable suggestions and summary
- **Semantic Similarity Score:** Measures how well your resume matches the JD
- **Skill Overlap Chart:** Visual bar chart of matched vs unmatched skills
- **Word Cloud:** Visualizes important JD keywords
- **Executive Summary Card:** Quick verdict and badge
- **Tabs:** Overview, Skills, Suggestions, Summary
- **PDF Report:** Downloadable summary of your results
- **Sidebar Tips & FAQ:** Best practices and help
- **Modern, Responsive UI**

## Tech Stack
- **Frontend:** Streamlit
- **AI Feedback:** Google Gemini API (`google-generativeai`)
- **Semantic Similarity:** `sentence-transformers` (MiniLM)
- **NLP:** spaCy
- **Visualization:** Plotly, WordCloud
- **PDF:** reportlab

## Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone <repo-url>
   cd Resume-Screening
   ```
2. **Create a Virtual Environment (Recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```
4. **Download spaCy Model**
   ```bash
   python -m spacy download en_core_web_sm
   ```
5. **Set up Gemini API Key**
   - Get your key from [Google AI Studio](https://aistudio.google.com/app/apikey)
   - Add to `.env`:
     ```
     GEMINI_API_KEY=your-gemini-api-key-here
     ```
6. **Run the App**
   ```bash
   streamlit run app.py
   ```

## Usage
- Upload your resume and job description (PDF or DOCX)
- View the executive summary, skill overlap, suggestions, and feedback
- Download your personalized PDF report

## Screenshots
_Add screenshots of the UI, charts, and PDF report here._

## File Structure
```
app.py                  # Streamlit app
resume_parser.py        # Resume & JD text extraction
ats_matcher.py          # Keyword extraction
semantic_matcher.py     # Semantic similarity logic
feedback_generator.py   # Gemini AI feedback
requirements.txt        # Dependencies
README.md               # This file
```

## License
MIT 