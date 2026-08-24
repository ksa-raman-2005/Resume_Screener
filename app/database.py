import sqlite3
import json
import os
import uuid
from typing import Dict, Any, List, Optional

DB_PATH = os.environ.get("DB_PATH", "screener.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Enable WAL mode for better concurrency
    cursor.execute("PRAGMA journal_mode=WAL;")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS jobs (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        company TEXT,
        jd_text TEXT NOT NULL,
        parsed_requirements TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS candidates (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT,
        phone TEXT,
        skills TEXT,
        experience_years REAL DEFAULT 0,
        education TEXT,
        projects TEXT,
        raw_text TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS evaluations (
        id TEXT PRIMARY KEY,
        job_id TEXT NOT NULL,
        candidate_id TEXT NOT NULL,
        overall_score REAL NOT NULL,
        skill_score REAL NOT NULL,
        semantic_score REAL NOT NULL,
        strengths TEXT,
        gaps TEXT,
        justification TEXT,
        interview_questions TEXT,
        status TEXT NOT NULL,
        evaluated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (job_id) REFERENCES jobs(id),
        FOREIGN KEY (candidate_id) REFERENCES candidates(id)
    );
    """)
    
    conn.commit()
    conn.close()

def save_job(title: str, company: str, jd_text: str, parsed_requirements: Dict[str, Any]) -> str:
    job_id = str(uuid.uuid4())
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO jobs (id, title, company, jd_text, parsed_requirements) VALUES (?, ?, ?, ?, ?)",
        (job_id, title, company, jd_text, json.dumps(parsed_requirements))
    )
    conn.commit()
    conn.close()
    return job_id

def save_candidate(name: str, email: str, phone: str, skills: List[str], experience_years: float, education: List[Dict[str, Any]], projects: List[Dict[str, Any]], raw_text: str) -> str:
    candidate_id = str(uuid.uuid4())
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO candidates (id, name, email, phone, skills, experience_years, education, projects, raw_text) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (candidate_id, name, email, phone, json.dumps(skills), experience_years, json.dumps(education), json.dumps(projects), raw_text)
    )
    conn.commit()
    conn.close()
    return candidate_id

def save_evaluation(job_id: str, candidate_id: str, overall_score: float, skill_score: float, semantic_score: float, strengths: List[str], gaps: List[str], justification: str, interview_questions: List[str], status: str) -> str:
    eval_id = str(uuid.uuid4())
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO evaluations 
           (id, job_id, candidate_id, overall_score, skill_score, semantic_score, strengths, gaps, justification, interview_questions, status)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (eval_id, job_id, candidate_id, overall_score, skill_score, semantic_score, json.dumps(strengths), json.dumps(gaps), justification, json.dumps(interview_questions), status)
    )
    conn.commit()
    conn.close()
    return eval_id

def get_evaluations_for_job(job_id: str) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    query = """
    SELECT e.*, c.name as candidate_name, c.email as candidate_email, c.phone as candidate_phone, c.skills as candidate_skills, c.experience_years
    FROM evaluations e
    JOIN candidates c ON e.candidate_id = c.id
    WHERE e.job_id = ?
    ORDER BY e.overall_score DESC
    """
    cursor.execute(query, (job_id,))
    rows = cursor.fetchall()
    conn.close()
    
    results = []
    for r in rows:
        item = dict(r)
        item['strengths'] = json.loads(item['strengths']) if item['strengths'] else []
        item['gaps'] = json.loads(item['gaps']) if item['gaps'] else []
        item['interview_questions'] = json.loads(item['interview_questions']) if item['interview_questions'] else []
        item['candidate_skills'] = json.loads(item['candidate_skills']) if item['candidate_skills'] else []
        results.append(item)
    return results

def get_all_candidates() -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email, phone, skills, experience_years, created_at FROM candidates ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    
    results = []
    for r in rows:
        item = dict(r)
        item['skills'] = json.loads(item['skills']) if item['skills'] else []
        results.append(item)
    return results
