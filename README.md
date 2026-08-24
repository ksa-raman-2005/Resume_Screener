# Smart Resume Screener 🚀

[![Live Demo](https://img.shields.io/badge/Render-Live_App-brightgreen?style=for-the-badge&logo=render)](https://smart-resume-screener-26vp.onrender.com/)
[![GitHub Repo](https://img.shields.io/badge/GitHub-Repository-blue?style=for-the-badge&logo=github)](https://github.com/ksa-raman-2005/Resume_Screener)

An executive-grade talent intelligence platform designed to parse candidate resumes, extract normalized domain skills, and evaluate candidate alignment against Job Descriptions using a **Tri-Tier Hybrid Matching Engine**.

---

## 🔗 Live Application Links

* **Live Deployment (Render):** [https://smart-resume-screener-26vp.onrender.com/](https://smart-resume-screener-26vp.onrender.com/)
* **GitHub Repository:** [https://github.com/ksa-raman-2005/Resume_Screener](https://github.com/ksa-raman-2005/Resume_Screener)
* **Local Server URL:** `http://localhost:8000`

---

## 🎯 Key Features & Core Capabilities

* **Multi-Format Document Parsing:** Native drag-and-drop extraction for `.pdf`, `.docx`, `.doc`, and `.txt` files without requiring text copy-pasting.
* **Distinct Candidate Profiles:** Evaluates each resume independently (zero profile merging), displaying individual match percentages, extracted skills, and custom insights.
* **Tri-Tier Hybrid Screener Engine:**
  * **Tier 1 (Taxonomy & Alias Normalizer):** Standardizes technical aliases across stacks (e.g., `React.js` -> `React`, `Postgres` -> `PostgreSQL`, `K8s` -> `Kubernetes`).
  * **Tier 2 (TF-IDF Vector Cosine Similarity):** Quantifies statistical text overlap between project experience and job responsibilities.
  * **Tier 3 (Structured LLM Diagnostic):** Generates qualitative alignment justifications, identifies critical skill gaps, and formulates candidate-specific technical interview questions.
* **Executive Dashboard UI:** Clean interface with drag-and-drop batch file uploads, real-time shortlist rankings, candidate diagnostic drawers, and dynamic Light/Dark mode switching.

---

## 🏗 System Architecture

The project pairs a high-performance Python backend with an embedded serverless database:

```text
               +----------------------------------+
               |   Multi-Format File Ingestion    |
               |     (PDF, DOCX, DOC, TXT)        |
               +----------------------------------+
                                |
                                v
               +----------------------------------+
               |  Tier 1: Taxonomy Normalizer     |
               |  (Alias Mapping & Standardizing) |
               +----------------------------------+
                                |
                                v
               +----------------------------------+
               |  Tier 2: TF-IDF Cosine Vector     |
               |  (Statistical Skill Match Ratio) |
               +----------------------------------+
                                |
                                v
               +----------------------------------+
               |  Tier 3: LLM Diagnostic Engine   |
               |  (Gaps, Strengths & Questions)   |
               +----------------------------------+
                                |
                                v
               +----------------------------------+
               |      SQLite 3 Database (WAL)     |
               | (Jobs, Candidates, Evaluations)  |
               +----------------------------------+
