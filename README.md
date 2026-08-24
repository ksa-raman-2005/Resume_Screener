# Smart Resume Screener

An executive, high-precision talent intelligence platform that parses resumes, extracts domain skills, and screens candidates against Job Descriptions using a **Tri-Tier Hybrid Matching Engine** (Taxonomy Normalization + TF-IDF Vector Cosine Similarity + LLM Justification & Diagnostic Analysis).

Target Repository: `https://github.com/ksa-raman-2005/Resume_Screener`

---

## Key Features

- **Multi-Format Input Support**: Upload Job Descriptions and Candidate Resumes in PDF format or paste raw plain text directly.
- **Group / Batch Candidate Upload**: Select and screen multiple candidate PDF resumes simultaneously in a single evaluation session.
- **Tri-Tier Precision Screening**:
  - **Tier 1 (Taxonomy & Alias Normalizer)**: Maps technology variations (`React.js` $\leftrightarrow$ `React`, `Postgres` $\leftrightarrow$ `PostgreSQL`, `K8s` $\leftrightarrow$ `Kubernetes`).
  - **Tier 2 (TF-IDF Vector Cosine Similarity)**: Measures semantic text overlap between candidate projects and JD responsibilities.
  - **Tier 3 (Structured LLM Diagnostic)**: Generates overall weighted match scores, highlights verified strengths vs missing skill gaps, and formulates candidate-specific technical interview questions.
- **No Candidate Left Behind**: Semantic equivalence matching ensures top candidates are never rejected simply due to keyword phrasing differences.
- **Executive Professional UI**:
  - Native **Light & Dark Theme** toggle (persistent setting stored in `localStorage`).
  - **Strictly Emoji-Free**: Designed with clean typography and crisp inline SVG icons.
  - Candidate shortlist table with ranking, score badges, status filters, and interactive candidate detail drawer.

---

## Database Architecture & Storage

### Database Used: **SQLite 3** (`screener.db`)

The application utilizes an embedded, serverless **SQLite 3** database with Write-Ahead Logging (WAL) enabled for high-performance concurrent reads and zero memory bloat.

### Schema Structure:

1. **`jobs` Table**:
   - `id` (TEXT PRIMARY KEY) - UUID identifier.
   - `title` (TEXT) - Extracted job title.
   - `company` (TEXT) - Hiring company.
   - `jd_text` (TEXT) - Raw job description text.
   - `parsed_requirements` (TEXT) - JSON string of extracted skills and experience requirements.
   - `created_at` (DATETIME) - Timestamp.

2. **`candidates` Table**:
   - `id` (TEXT PRIMARY KEY) - UUID identifier.
   - `name` (TEXT) - Candidate name.
   - `email` (TEXT) - Extracted contact email.
   - `phone` (TEXT) - Extracted phone number.
   - `skills` (TEXT) - JSON list of extracted technical skills.
   - `experience_years` (REAL) - Estimated years of experience.
   - `education` (TEXT) - JSON list of educational qualifications.
   - `projects` (TEXT) - JSON list of domain project descriptions.
   - `raw_text` (TEXT) - Complete extracted resume text.

3. **`evaluations` Table**:
   - `id` (TEXT PRIMARY KEY) - UUID identifier.
   - `job_id` (FOREIGN KEY -> `jobs.id`)
   - `candidate_id` (FOREIGN KEY -> `candidates.id`)
   - `overall_score` (REAL) - Composite score (0 - 100%).
   - `skill_score` (REAL) - Skill overlap matrix score.
   - `semantic_score` (REAL) - TF-IDF vector similarity score.
   - `strengths` (TEXT) - JSON array of matching skills/strengths.
   - `gaps` (TEXT) - JSON array of missing critical skills.
   - `justification` (TEXT) - Executive hiring summary.
   - `interview_questions` (TEXT) - JSON array of candidate-specific interview questions.
   - `status` (TEXT) - `Shortlisted`, `Under Review`, or `Not Shortlisted`.

---

## Clean Repository Standard (Excluded Files)

The project `.gitignore` strictly excludes unnecessary or sensitive files:
- `node_modules/` or virtual environments (`venv/`, `.venv/`)
- `.env` or sensitive configuration files
- Build artifacts (`dist/`, `.next/`, `out/`, `build/`)
- SQLite runtime databases (`screener.db`, `*.sqlite`)
- Temporary/editor settings (`.vscode/`, `.idea/`, `.DS_Store`)

---

## Auto-Deployment Guide (Render Free Tier)

This application is ready for auto-deployment on Render using the included `render.yaml` blueprint.

### Deployment Steps:

1. **Push Code to GitHub**:
   Push this repository to `https://github.com/ksa-raman-2005/Resume_Screener`.

2. **Deploy on Render**:
   - Log into [Render Dashboard](https://dashboard.render.com).
   - Click **New +** -> **Blueprint**.
   - Connect your GitHub repository `ksa-raman-2005/Resume_Screener`.
   - Render will automatically read `render.yaml` and configure:
     - **Service Type**: Web Service (Python 3.11)
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - *(Optional)* Add Environment Variable:
     - `GEMINI_API_KEY`: Your Google Gemini API Key (If omitted, the app automatically runs the deterministic Tier-1/2 heuristic screener).

3. **Access Application**:
   Render will provide a live HTTPS URL (e.g. `https://smart-resume-screener.onrender.com`).

---

## Local Development Setup

```bash
# 1. Clone repo
git clone https://github.com/ksa-raman-2005/Resume_Screener.git
cd Resume_Screener

# 2. Create virtual environment & install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Launch dev server
python3 -m uvicorn app.main:app --reload --port 8000
```
Open `http://localhost:8000` in your web browser.
