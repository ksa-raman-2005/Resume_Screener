import os
import json
from typing import Dict, Any
from app.screener import evaluate_candidate_heuristic

def evaluate_candidate_with_llm(candidate: Dict[str, Any], job: Dict[str, Any], api_key: str = None) -> Dict[str, Any]:
    """Evaluates candidate using Google Gemini API if key is present, otherwise falls back to heuristic engine."""
    effective_key = api_key or os.environ.get("GEMINI_API_KEY")
    
    # Fallback if no API key is available
    if not effective_key:
        print("No GEMINI_API_KEY configured. Utilizing Tier-1 & Tier-2 Heuristic Screener.")
        return evaluate_candidate_heuristic(candidate, job)
        
    try:
        from google import genai
        client = genai.Client(api_key=effective_key)
        
        prompt = f"""
You are an expert HR Intelligence Screener evaluating a candidate for a job opening.

Job Description:
Title: {job.get('title')}
Required Skills: {', '.join(job.get('required_skills', []))}
Full Text:
{job.get('raw_text', '')[:1500]}

Candidate Profile:
Name: {candidate.get('name')}
Extracted Skills: {', '.join(candidate.get('skills', []))}
Experience Years: {candidate.get('experience_years')}
Full Resume Text:
{candidate.get('raw_text', '')[:1500]}

Perform a strict semantic matching and risk analysis.
Return ONLY a JSON object matching this exact schema:
{{
  "overall_score": float (0-100),
  "skill_score": float (0-100),
  "semantic_score": float (0-100),
  "strengths": [list of top matching skills/strengths],
  "gaps": [list of missing skills or experience gaps],
  "justification": "Clear, objective 2-3 sentence hiring justification explaining why candidate fits or fails requirements.",
  "interview_questions": [3 specific technical interview questions based on candidate's gaps or projects],
  "status": "Shortlisted" | "Under Review" | "Not Shortlisted"
}}
"""
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        
        raw_output = response.text.strip()
        # Clean JSON markdown if wrapped in ```json ... ```
        if "```" in raw_output:
            raw_output = raw_output.split("```")[1]
            if raw_output.startswith("json"):
                raw_output = raw_output[4:]
        raw_output = raw_output.strip()
        
        parsed = json.loads(raw_output)
        return {
            "overall_score": float(parsed.get("overall_score", 70.0)),
            "skill_score": float(parsed.get("skill_score", 70.0)),
            "semantic_score": float(parsed.get("semantic_score", 70.0)),
            "strengths": list(parsed.get("strengths", [])),
            "gaps": list(parsed.get("gaps", [])),
            "justification": str(parsed.get("justification", "")),
            "interview_questions": list(parsed.get("interview_questions", [])),
            "status": str(parsed.get("status", "Under Review"))
        }
    except Exception as e:
        print(f"LLM API call error, defaulting to heuristic engine: {e}")
        return evaluate_candidate_heuristic(candidate, job)
