import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import spacy
nlp = spacy.load("en_core_web_sm")


def extract_keywords(text):
    """Extract keywords (nouns, skills, tools) from text using spaCy."""
    doc = nlp(text)
    keywords = set()
    for token in doc:
        if token.pos_ in ["NOUN", "PROPN"] and not token.is_stop and len(token.text) > 2:
            keywords.add(token.lemma_.lower())
    return list(keywords)


def compute_tfidf_score(resume_text, jd_text):
    """Compute cosine similarity between resume and JD using TF-IDF."""
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf = vectorizer.fit_transform([resume_text, jd_text])
    score = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
    return round(score * 100, 2)  # Return as percentage


def find_missing_keywords(resume_text, jd_text):
    """Find keywords present in JD but missing in resume."""
    resume_keywords = set(extract_keywords(resume_text))
    jd_keywords = set(extract_keywords(jd_text))
    missing = jd_keywords - resume_keywords
    return list(missing) 
