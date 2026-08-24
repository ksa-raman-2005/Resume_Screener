import math
import re
from collections import Counter
from typing import Dict, Any, List, Tuple
from app.parser import normalize_skill

def compute_tf_idf_similarity(jd_text: str, candidate_text: str) -> float:
    """Computes TF-IDF vector cosine similarity between job description and resume text."""
    if not jd_text.strip() or not candidate_text.strip():
        return 0.0
    
    # Try using scikit-learn if available
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))
        tfidf_matrix = vectorizer.fit_transform([jd_text, candidate_text])
        sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        return round(float(sim) * 100, 1)
    except Exception:
        # Pure Python fallback for TF-IDF & Cosine Similarity
        def tokenize(text):
            return re.findall(r'\b[a-zA-Z0-9+#.]{2,}\b', text.lower())
        
        words1 = tokenize(jd_text)
        words2 = tokenize(candidate_text)
        
        tf1 = Counter(words1)
        tf2 = Counter(words2)
        
        all_words = set(words1).union(set(words2))
        if not all_words:
            return 50.0
            
        dot_product = 0.0
        mag1 = 0.0
        mag2 = 0.0
        
        for word in all_words:
            v1 = tf1.get(word, 0)
            v2 = tf2.get(word, 0)
            # IDF weight heuristic (words in both get standard weight)
            idf = 1.0 if (v1 > 0 and v2 > 0) else 0.5
            w1 = v1 * idf
            w2 = v2 * idf
            dot_product += w1 * w2
            mag1 += w1 ** 2
            mag2 += w2 ** 2
            
        if mag1 == 0 or mag2 == 0:
            return 0.0
            
        cosine = dot_product / (math.sqrt(mag1) * math.sqrt(mag2))
        return round(float(cosine) * 100, 1)

def compute_skill_overlap(jd_skills: List[str], candidate_skills: List[str]) -> Tuple[float, List[str], List[str]]:
    """Calculates skill match percentage, matched strengths, and missing gaps."""
    if not jd_skills:
        return 80.0, candidate_skills, []
    
    cand_skill_set = {s.lower() for s in candidate_skills}
    matched = []
    missing = []
    
    for req in jd_skills:
        req_norm = req.lower()
        if req_norm in cand_skill_set or any(req_norm in s or s in req_norm for s in cand_skill_set):
            matched.append(req)
        else:
            missing.append(req)
            
    match_ratio = len(matched) / len(jd_skills) if jd_skills else 1.0
    skill_score = round(match_ratio * 100, 1)
    
    return skill_score, matched, missing

def evaluate_candidate_heuristic(candidate: Dict[str, Any], job: Dict[str, Any]) -> Dict[str, Any]:
    """Hybrid screening engine using TF-IDF + Skill Matrix heuristics."""
    jd_skills = job.get("required_skills", [])
    cand_skills = candidate.get("skills", [])
    
    skill_score, strengths, gaps = compute_skill_overlap(jd_skills, cand_skills)
    semantic_score = compute_tf_idf_similarity(job.get("raw_text", ""), candidate.get("raw_text", ""))
    
    # Base weighted score
    overall_score = round((0.55 * skill_score) + (0.45 * semantic_score), 1)
    
    # Experience penalty / bonus check
    min_exp = job.get("min_experience_years", 0)
    cand_exp = candidate.get("experience_years", 0)
    if cand_exp >= min_exp and min_exp > 0:
        overall_score = min(100.0, overall_score + 3.0)
    elif min_exp > 0 and cand_exp < (min_exp / 2):
        overall_score = max(0.0, overall_score - 5.0)
        
    overall_score = round(overall_score, 1)
    
    # Status determination
    if overall_score >= 75.0:
        status = "Shortlisted"
    elif overall_score >= 55.0:
        status = "Under Review"
    else:
        status = "Not Shortlisted"
        
    # Generate structured justification
    justification_parts = [
        f"Candidate {candidate.get('name', 'Applicant')} achieved an overall match score of {overall_score}%.",
        f"Demonstrates technical competence in: {', '.join(strengths[:5]) if strengths else 'core engineering practices'}.",
    ]
    if gaps:
        justification_parts.append(f"Identified skill gaps in key requirements: {', '.join(gaps[:4])}.")
    else:
        justification_parts.append("Meets all explicitly listed technical skill requirements.")
        
    if cand_exp > 0:
        justification_parts.append(f"Brings ~{cand_exp} years of relevant experience.")
        
    justification = " ".join(justification_parts)
    
    # Generate candidate-specific interview question prompts based on gaps and skills
    interview_questions = []
    if gaps:
        for g in gaps[:2]:
            interview_questions.append(f"The position requires {g}. Can you walk us through your familiarity or hands-on exposure with {g}?")
    if strengths:
        interview_questions.append(f"You listed expertise in {strengths[0]}. How have you applied {strengths[0]} in your recent projects?")
    interview_questions.append("Can you describe a challenging engineering problem you solved in your recent role?")
    
    return {
        "overall_score": overall_score,
        "skill_score": skill_score,
        "semantic_score": semantic_score,
        "strengths": strengths if strengths else cand_skills[:5],
        "gaps": gaps,
        "justification": justification,
        "interview_questions": interview_questions[:3],
        "status": status
    }
