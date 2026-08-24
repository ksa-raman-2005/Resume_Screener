import os
from typing import List, Optional
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Header
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from app.database import (
    init_db, save_job, save_candidate, save_evaluation, 
    get_evaluations_for_job, get_all_candidates
)
from app.parser import (
    extract_text_from_pdf_bytes, parse_resume, parse_job_description
)
from app.llm import evaluate_candidate_with_llm

app = FastAPI(
    title="Smart Resume Screener",
    description="Intelligent resume screening & candidate matching engine powered by SQLite and Hybrid Semantic Matching.",
    version="1.0.0"
)

# Mount static directory for frontend web UI
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.on_event("startup")
def startup_event():
    init_db()

@app.get("/")
def read_root():
    index_file = os.path.join(static_dir, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "Smart Resume Screener API operational."}

@app.get("/api/health")
def health_check():
    return {"status": "ok", "database": "SQLite initialized"}

@app.post("/api/screen")
async def screen_resumes(
    jd_text: Optional[str] = Form(None),
    jd_file: Optional[UploadFile] = File(None),
    resume_texts: Optional[List[str]] = Form(None),
    resume_files: Optional[List[UploadFile]] = File(None),
    x_api_key: Optional[str] = Header(None)
):
    """Processes Job Description + multiple candidate resumes (PDF or Text), extracts structured data, and runs semantic match evaluation."""
    # 1. Resolve Job Description Text
    final_jd_text = ""
    if jd_file and jd_file.filename:
        content = await jd_file.read()
        if jd_file.filename.lower().endswith(".pdf"):
            final_jd_text = extract_text_from_pdf_bytes(content)
        else:
            final_jd_text = content.decode("utf-8", errors="ignore")
    elif jd_text:
        final_jd_text = jd_text
        
    if not final_jd_text.strip():
        raise HTTPException(status_code=400, detail="Job Description input is required (either text or PDF file).")
        
    parsed_job = parse_job_description(final_jd_text)
    job_id = save_job(parsed_job["title"], parsed_job["company"], final_jd_text, parsed_job)
    
    # 2. Extract Candidate Resumes
    candidate_sources = [] # list of raw_text strings
    
    # Process text inputs if provided
    if resume_texts:
        for txt in resume_texts:
            if txt and txt.strip():
                candidate_sources.append(txt.strip())
                
    # Process file uploads if provided
    if resume_files:
        for file_item in resume_files:
            if file_item and file_item.filename:
                content = await file_item.read()
                if file_item.filename.lower().endswith(".pdf"):
                    extracted = extract_text_from_pdf_bytes(content)
                else:
                    extracted = content.decode("utf-8", errors="ignore")
                if extracted.strip():
                    candidate_sources.append(extracted.strip())
                    
    if not candidate_sources:
        raise HTTPException(status_code=400, detail="At least one valid resume (PDF file or text) must be provided.")
        
    # 3. Process & Screen Candidates
    evaluations_result = []
    
    for raw_resume_text in candidate_sources:
        parsed_cand = parse_resume(raw_resume_text)
        cand_id = save_candidate(
            parsed_cand["name"],
            parsed_cand["email"],
            parsed_cand["phone"],
            parsed_cand["skills"],
            parsed_cand["experience_years"],
            parsed_cand["education"],
            parsed_cand["projects"],
            raw_resume_text
        )
        
        # Run hybrid evaluation
        eval_output = evaluate_candidate_with_llm(parsed_cand, parsed_job, api_key=x_api_key)
        
        eval_id = save_evaluation(
            job_id=job_id,
            candidate_id=cand_id,
            overall_score=eval_output["overall_score"],
            skill_score=eval_output["skill_score"],
            semantic_score=eval_output["semantic_score"],
            strengths=eval_output["strengths"],
            gaps=eval_output["gaps"],
            justification=eval_output["justification"],
            interview_questions=eval_output["interview_questions"],
            status=eval_output["status"]
        )
        
        evaluations_result.append({
            "evaluation_id": eval_id,
            "candidate_id": cand_id,
            "candidate_name": parsed_cand["name"],
            "candidate_email": parsed_cand["email"],
            "candidate_phone": parsed_cand["phone"],
            "candidate_skills": parsed_cand["skills"],
            "experience_years": parsed_cand["experience_years"],
            "overall_score": eval_output["overall_score"],
            "skill_score": eval_output["skill_score"],
            "semantic_score": eval_output["semantic_score"],
            "strengths": eval_output["strengths"],
            "gaps": eval_output["gaps"],
            "justification": eval_output["justification"],
            "interview_questions": eval_output["interview_questions"],
            "status": eval_output["status"]
        })
        
    # Sort candidate results by overall score descending
    evaluations_result.sort(key=lambda x: x["overall_score"], reverse=True)
    
    return {
        "job_id": job_id,
        "job_title": parsed_job["title"],
        "required_skills": parsed_job["required_skills"],
        "total_evaluated": len(evaluations_result),
        "candidates": evaluations_result
    }

@app.get("/api/candidates")
def list_candidates():
    """Retrieve all historical candidates stored in SQLite database."""
    return {"candidates": get_all_candidates()}

@app.get("/api/job/{job_id}/evaluations")
def get_job_evaluations(job_id: str):
    """Retrieve evaluations for a specific job session."""
    evals = get_evaluations_for_job(job_id)
    return {"job_id": job_id, "evaluations": evals}
