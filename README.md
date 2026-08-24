# Smart Resume Screener

An executive, high-precision talent intelligence platform that parses resumes, extracts domain skills, and screens candidates against Job Descriptions using a **Tri-Tier Hybrid Matching Engine** (Taxonomy Normalization + TF-IDF Vector Cosine Similarity + LLM Justification & Diagnostic Analysis).

### 🚀 Live Render Deployment Link
**Live Web Application**: [https://smart-resume-screener-26vp.onrender.com/](https://smart-resume-screener-26vp.onrender.com/)

**GitHub Repository**: [https://github.com/ksa-raman-2005/Resume_Screener](https://github.com/ksa-raman-2005/Resume_Screener)

---

## Render Free Tier Auto-Deploy Setup (1-Minute Guide)

The repository includes a ready-to-use [`render.yaml`](render.yaml) blueprint file for zero-configuration free tier hosting.

### Quick Deployment Steps:

1. Go to [Render Dashboard](https://dashboard.render.com).
2. Click **New +** -> **Blueprint**.
3. Select & Connect your GitHub Repository: `https://github.com/ksa-raman-2005/Resume_Screener`.
4. Render will read `render.yaml` and deploy automatically:
   - **Environment**: Python 3.11
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Your app will be live at: `https://smart-resume-screener.onrender.com` (or your assigned `.onrender.com` URL).

---

## Features

- **Multi-Format Upload**: Upload Job Descriptions & Candidate Resumes in PDF format, Word (`.docx`), or Plain Text.
- **Distinct Candidate Profiles**: Evaluates each candidate file separately (no merging), extracting contact info, skills, and experience.
- **Tri-Tier Hybrid Screener**:
  - **Tier 1 (Taxonomy & Alias Normalizer)**: Standardizes aliases (`React.js` $\leftrightarrow$ `React`, `Postgres` $\leftrightarrow$ `PostgreSQL`, `K8s` $\leftrightarrow$ `Kubernetes`).
  - **Tier 2 (TF-IDF Vector Cosine Similarity)**: Measures semantic text overlap between candidate projects and JD responsibilities.
  - **Tier 3 (Structured LLM Diagnostic)**: Generates composite scores, verified strengths vs missing skill gaps, and tailored technical interview questions.
- **Executive Professional UI**: Clean Light & Dark theme switcher, zero emojis, inline SVG icons, shortlist ranking table, and candidate diagnostic modal drawer.

---

## Database Architecture (`SQLite 3`)

Uses an embedded serverless **SQLite 3** database (`screener.db`) with Write-Ahead Logging (WAL) enabled:

- **`jobs`**: Stores job description text and extracted skills.
- **`candidates`**: Stores candidate profiles, contact info, parsed skills, projects, and education.
- **`evaluations`**: Stores match scores, skill/semantic matrices, strengths, gaps, hiring justifications, and generated interview question prompts.

---

## Clean Repository Standard

The `.gitignore` strictly excludes temporary and sensitive files:
- `node_modules/`, `venv/`, `.venv/`
- `.env` or configuration secrets
- Build artifacts (`dist/`, `.next/`, `out/`, `build/`)
- Local SQLite runtime database (`screener.db`)
- Editor settings (`.vscode/`, `.idea/`, `.DS_Store`)

---

## Local Development Setup

```bash
git clone https://github.com/ksa-raman-2005/Resume_Screener.git
cd Resume_Screener

pip install -r requirements.txt
python3 -m uvicorn app.main:app --reload --port 8000
```
Access locally at `http://localhost:8000`.
