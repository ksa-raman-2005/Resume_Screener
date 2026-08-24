import re
import io
from typing import Dict, Any, List, Tuple
from pypdf import PdfReader

# Master skill taxonomy dictionary for alias normalization
TAXONOMY_MAP = {
    "react": "React.js",
    "reactjs": "React.js",
    "react.js": "React.js",
    "node": "Node.js",
    "nodejs": "Node.js",
    "node.js": "Node.js",
    "python": "Python",
    "python3": "Python",
    "py": "Python",
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "k8s": "Kubernetes",
    "kubernetes": "Kubernetes",
    "aws": "AWS",
    "amazon web services": "AWS",
    "gcp": "Google Cloud",
    "google cloud": "Google Cloud",
    "docker": "Docker",
    "ts": "TypeScript",
    "typescript": "TypeScript",
    "js": "JavaScript",
    "javascript": "JavaScript",
    "cpp": "C++",
    "c++": "C++",
    "golang": "Go",
    "go": "Go",
    "fastapi": "FastAPI",
    "django": "Django",
    "flask": "Flask",
    "ml": "Machine Learning",
    "machine learning": "Machine Learning",
    "ai": "Artificial Intelligence",
    "artificial intelligence": "Artificial Intelligence",
    "nlp": "Natural Language Processing",
    "sql": "SQL",
    "nosql": "NoSQL",
    "mongodb": "MongoDB",
    "redis": "Redis",
    "graphql": "GraphQL",
    "rest": "REST API",
    "restful": "REST API",
    "git": "Git",
    "ci/cd": "CI/CD",
    "cicd": "CI/CD",
    "tailwinds": "Tailwind CSS",
    "tailwindcss": "Tailwind CSS",
    "tailwind": "Tailwind CSS",
}

COMMON_SKILLS_SET = set(TAXONOMY_MAP.values()).union({
    "HTML", "CSS", "Java", "C#", "Rust", "Swift", "Kotlin", "TensorFlow", "PyTorch",
    "Pandas", "NumPy", "Scikit-Learn", "Spark", "Hadoop", "System Design", "Microservices",
    "Agile", "Scrum", "Jira", "Linux", "Bash", "Shell", "Terraform", "Ansible"
})

def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    """Extract text clean from PDF bytes using pypdf."""
    try:
        reader = PdfReader(io.BytesIO(pdf_bytes))
        text_pages = []
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text_pages.append(extracted)
        return "\n".join(text_pages).strip()
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return ""

def normalize_skill(skill: str) -> str:
    cleaned = skill.strip().lower()
    return TAXONOMY_MAP.get(cleaned, skill.strip().title())

def extract_skills_from_text(text: str) -> List[str]:
    found_skills = set()
    lowered = text.lower()
    
    # 1. Match against known taxonomy map
    for raw_skill, normalized in TAXONOMY_MAP.items():
        pattern = r'\b' + re.escape(raw_skill) + r'\b'
        if re.search(pattern, lowered):
            found_skills.add(normalized)
            
    # 2. Match against common skills set
    for skill in COMMON_SKILLS_SET:
        pattern = r'\b' + re.escape(skill.lower()) + r'\b'
        if re.search(pattern, lowered):
            found_skills.add(skill)
            
    return sorted(list(found_skills))

def extract_email(text: str) -> str:
    match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
    return match.group(0) if match else ""

def extract_phone(text: str) -> str:
    match = re.search(r'\(?\+?[0-9]{1,3}\)?[-.\s]?[0-9]{3,4}[-.\s]?[0-9]{3,4}[-.\s]?[0-9]{3,4}', text)
    return match.group(0) if match else ""

def extract_name(text: str) -> str:
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    if not lines:
        return "Unknown Candidate"
    
    # First candidate line that doesn't contain email or website or common keywords
    for line in lines[:5]:
        if "@" in line or "http" in line or "resume" in line.lower() or "curriculum" in line.lower():
            continue
        cleaned = re.sub(r'[^a-zA-Z\s.]', '', line).strip()
        if 2 <= len(cleaned.split()) <= 4 and len(cleaned) < 40:
            return cleaned.title()
    return lines[0][:30].title()

def extract_experience_years(text: str) -> float:
    # Search for patterns like "5+ years", "3 yrs", "2019 - 2023"
    patterns = [
        r'(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)\s+(?:of\s+)?experience',
        r'experience\s*:\s*(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)'
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                pass
            
    # Year difference heuristics (e.g. 2018 - 2023)
    years = [int(y) for y in re.findall(r'\b(19[9\-]\d|20[0-2]\d)\b', text)]
    if len(years) >= 2:
        diff = max(years) - min(years)
        if 1 <= diff <= 35:
            return float(diff)
            
    return 1.0

def parse_resume(text: str) -> Dict[str, Any]:
    name = extract_name(text)
    email = extract_email(text)
    phone = extract_phone(text)
    skills = extract_skills_from_text(text)
    exp_years = extract_experience_years(text)
    
    # Extract projects section heuristics
    projects = []
    project_section_match = re.search(r'(?:projects|personal projects|key projects)([\s\S]*?)(?:education|certifications|experience|$)', text, re.IGNORECASE)
    if project_section_match:
        proj_text = project_section_match.group(1).strip()
        bullets = [p.strip() for p in proj_text.split('\n') if len(p.strip()) > 15]
        if bullets:
            projects.append({"title": "Key Projects & Domain Work", "description": " | ".join(bullets[:3])})
            
    # Extract education section heuristics
    education = []
    edu_match = re.search(r'(?:education|academic background)([\s\S]*?)(?:projects|experience|skills|$)', text, re.IGNORECASE)
    if edu_match:
        edu_text = edu_match.group(1).strip()
        lines = [line.strip() for line in edu_text.split('\n') if line.strip()]
        if lines:
            education.append({"degree": lines[0][:60], "institution": lines[1][:60] if len(lines) > 1 else ""})
            
    return {
        "name": name,
        "email": email,
        "phone": phone,
        "skills": skills,
        "experience_years": exp_years,
        "education": education,
        "projects": projects,
        "raw_text": text
    }

def parse_job_description(text: str) -> Dict[str, Any]:
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    title = lines[0] if lines else "Software Engineering Position"
    if len(title) > 60:
        title = title[:60] + "..."
        
    skills = extract_skills_from_text(text)
    exp_years = extract_experience_years(text)
    
    return {
        "title": title,
        "company": "Hiring Organization",
        "required_skills": skills,
        "min_experience_years": exp_years,
        "raw_text": text
    }
