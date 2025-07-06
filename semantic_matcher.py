from sentence_transformers import SentenceTransformer, util
import torch

def compute_semantic_similarity(resume_text: str, jd_text: str) -> float:
    """
    Returns a similarity score between 0 and 100 based on semantic understanding
    of resume and job description.
    """
    model = SentenceTransformer('all-MiniLM-L6-v2')
    resume_emb = model.encode(resume_text, convert_to_tensor=True)
    jd_emb = model.encode(jd_text, convert_to_tensor=True)
    sim = util.pytorch_cos_sim(resume_emb, jd_emb).item()
    score = round(sim * 100, 2)
    return score 