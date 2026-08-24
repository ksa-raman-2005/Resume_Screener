document.addEventListener('DOMContentLoaded', () => {
  // Theme Management
  const htmlEl = document.documentElement;
  const themeToggleBtn = document.getElementById('themeToggleBtn');
  const sunIcon = document.getElementById('sunIcon');
  const moonIcon = document.getElementById('moonIcon');

  const savedTheme = localStorage.getItem('theme') || 'dark';
  setTheme(savedTheme);

  themeToggleBtn.addEventListener('click', () => {
    const currentTheme = htmlEl.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    setTheme(newTheme);
  });

  function setTheme(theme) {
    htmlEl.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
    if (theme === 'light') {
      sunIcon.classList.add('hidden');
      moonIcon.classList.remove('hidden');
    } else {
      sunIcon.classList.remove('hidden');
      moonIcon.classList.add('hidden');
    }
  }

  // Tab Switchers (Upload File vs Paste Text)
  document.querySelectorAll('.tab-switcher').forEach(switcher => {
    switcher.addEventListener('click', (e) => {
      if (!e.target.classList.contains('tab-btn')) return;
      const targetId = e.target.getAttribute('data-target');
      
      const parentCol = switcher.closest('.form-column');
      parentCol.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      e.target.classList.add('active');

      parentCol.querySelectorAll('.tab-pane').forEach(pane => {
        if (pane.id === `${targetId}-pane`) {
          pane.classList.remove('hidden');
        } else {
          pane.classList.add('hidden');
        }
      });
    });
  });

  // Dropzone File Handlers
  const jdDropzone = document.getElementById('jdDropzone');
  const jdFileInput = document.getElementById('jdFileInput');
  const jdFileSelected = document.getElementById('jdFileSelected');

  const resumeDropzone = document.getElementById('resumeDropzone');
  const resumeFileInput = document.getElementById('resumeFileInput');
  const resumeFilesSelectedList = document.getElementById('resumeFilesSelectedList');

  jdFileInput.addEventListener('change', () => {
    if (jdFileInput.files.length > 0) {
      jdFileSelected.textContent = jdFileInput.files[0].name;
      jdFileSelected.classList.remove('hidden');
    }
  });

  setupDropzone(jdDropzone, jdFileInput, (files) => {
    if (files.length > 0) {
      jdFileInput.files = files;
      jdFileSelected.textContent = files[0].name;
      jdFileSelected.classList.remove('hidden');
    }
  });

  resumeFileInput.addEventListener('change', updateResumeFileList);
  setupDropzone(resumeDropzone, resumeFileInput, (files) => {
    resumeFileInput.files = files;
    updateResumeFileList();
  });

  function updateResumeFileList() {
    resumeFilesSelectedList.innerHTML = '';
    const files = resumeFileInput.files;
    if (files.length > 0) {
      Array.from(files).forEach(f => {
        const tag = document.createElement('span');
        tag.className = 'file-name-tag';
        tag.textContent = f.name;
        resumeFilesSelectedList.appendChild(tag);
      });
    }
  }

  function setupDropzone(dropzoneEl, inputEl, onDropCallback) {
    ['dragenter', 'dragover'].forEach(eventName => {
      dropzoneEl.addEventListener(eventName, (e) => {
        e.preventDefault();
        dropzoneEl.classList.add('dragover');
      }, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
      dropzoneEl.addEventListener(eventName, (e) => {
        e.preventDefault();
        dropzoneEl.classList.remove('dragover');
      }, false);
    });

    dropzoneEl.addEventListener('drop', (e) => {
      const dt = e.dataTransfer;
      const files = dt.files;
      onDropCallback(files);
    });
  }

  // Form Submission
  const screeningForm = document.getElementById('screeningForm');
  const submitBtn = document.getElementById('submitBtn');
  const resultsSection = document.getElementById('resultsSection');
  const candidateTableBody = document.getElementById('candidateTableBody');
  const jobTitleHeader = document.getElementById('jobTitleHeader');
  const evaluationMetaHeader = document.getElementById('evaluationMetaHeader');

  let currentEvaluations = [];

  screeningForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    // Determine active tabs
    const jdTabActive = document.querySelector('[data-target="jd-file"]').classList.contains('active');
    const resumeTabActive = document.querySelector('[data-target="resume-file"]').classList.contains('active');

    const jdText = document.getElementById('jdTextArea').value.trim();
    const resumeText = document.getElementById('resumeTextArea').value.trim();

    const formData = new FormData();

    if (jdTabActive && jdFileInput.files.length > 0) {
      formData.append('jd_file', jdFileInput.files[0]);
    } else if (jdText) {
      formData.append('jd_text', jdText);
    } else {
      alert("Please upload a Job Description file or paste the JD text.");
      return;
    }

    if (!resumeTabActive && resumeText) {
      formData.append('resume_texts', resumeText);
    } else if (resumeFileInput.files.length > 0) {
      Array.from(resumeFileInput.files).forEach(file => {
        formData.append('resume_files', file);
      });
    } else {
      alert("Please upload candidate PDF resume(s) or paste candidate text.");
      return;
    }

    // Submit state
    submitBtn.disabled = true;
    submitBtn.innerHTML = `
      <svg class="spinner" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12a9 9 0 1 1-6.219-8.56"/></svg>
      Screening Resumes...
    `;

    try {
      const response = await fetch('/api/screen', {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || 'Screening failed');
      }

      const data = await response.json();
      currentEvaluations = data.candidates;
      
      jobTitleHeader.textContent = `Shortlisted Candidates for: ${data.job_title}`;
      evaluationMetaHeader.textContent = `Evaluated ${data.total_evaluated} distinct candidate(s) against required competencies.`;
      
      renderCandidates(currentEvaluations);
      resultsSection.classList.remove('hidden');
      resultsSection.scrollIntoView({ behavior: 'smooth' });

    } catch (err) {
      alert(`Screening Error: ${err.message}`);
    } finally {
      submitBtn.disabled = false;
      submitBtn.innerHTML = `
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
        Screen Resumes
      `;
    }
  });

  // Filter Buttons
  const filterBtns = document.querySelectorAll('.filter-btn');
  filterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      filterBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const filter = btn.getAttribute('data-filter');
      if (filter === 'all') {
        renderCandidates(currentEvaluations);
      } else {
        const filtered = currentEvaluations.filter(c => c.status === filter);
        renderCandidates(filtered);
      }
    });
  });

  function renderCandidates(candidates) {
    candidateTableBody.innerHTML = '';
    
    if (candidates.length === 0) {
      candidateTableBody.innerHTML = `<tr><td colspan="7" style="text-align:center; padding: 24px; color: var(--text-muted);">No candidates match the selected filter.</td></tr>`;
      return;
    }

    candidates.forEach((c, idx) => {
      const tr = document.createElement('tr');
      tr.className = 'candidate-row';

      const scoreClass = c.overall_score >= 75 ? 'high' : (c.overall_score >= 55 ? 'mid' : 'low');
      const statusClass = c.status.replace(/\s+/g, '');

      tr.innerHTML = `
        <td>
          <span class="rank-badge">#${idx + 1}</span>
          <span class="cand-name">${escapeHtml(c.candidate_name)}</span>
        </td>
        <td style="font-size:0.8rem; color:var(--text-secondary);">${escapeHtml(c.filename || 'Uploaded Resume')}</td>
        <td>~${c.experience_years} yrs</td>
        <td>${renderSkillsPills(c.candidate_skills)}</td>
        <td><span class="score-pill ${scoreClass}">${c.overall_score}%</span></td>
        <td><span class="status-pill ${statusClass}">${escapeHtml(c.status)}</span></td>
        <td>
          <button class="btn btn-secondary icon-btn view-detail-btn" data-id="${c.candidate_id}" title="View Diagnostics">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
          </button>
        </td>
      `;

      candidateTableBody.appendChild(tr);
    });

    document.querySelectorAll('.view-detail-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const candId = btn.getAttribute('data-id');
        const candidate = currentEvaluations.find(item => item.candidate_id === candId);
        if (candidate) openModal(candidate);
      });
    });
  }

  function renderSkillsPills(skills) {
    if (!skills || skills.length === 0) return '<span style="color:var(--text-muted);">None</span>';
    return skills.slice(0, 3).map(s => `<span class="pill badge-neutral" style="margin-right:4px;">${escapeHtml(s)}</span>`).join('') + (skills.length > 3 ? `<span style="font-size:0.75rem; color:var(--text-muted);">+${skills.length - 3}</span>` : '');
  }

  // Modal Handling
  const candidateModal = document.getElementById('candidateModal');
  const closeModalBtn = document.getElementById('closeModalBtn');

  closeModalBtn.addEventListener('click', closeModal);
  candidateModal.addEventListener('click', (e) => {
    if (e.target === candidateModal) closeModal();
  });

  function openModal(c) {
    document.getElementById('modalCandidateName').textContent = c.candidate_name;
    document.getElementById('modalCandidateSub').textContent = `File: ${c.filename || 'Uploaded Resume'} | Status: ${c.status}`;
    
    document.getElementById('modalOverallScore').textContent = `${c.overall_score}%`;
    document.getElementById('modalSkillScore').textContent = `${c.skill_score}%`;
    document.getElementById('modalSemanticScore').textContent = `${c.semantic_score}%`;

    document.getElementById('modalJustificationText').textContent = c.justification;

    const strContainer = document.getElementById('modalStrengthsContainer');
    strContainer.innerHTML = c.strengths.length > 0 
      ? c.strengths.map(s => `<span class="pill pill-strength">${escapeHtml(s)}</span>`).join('')
      : '<span style="font-size:0.85rem; color:var(--text-muted);">No key strengths identified</span>';

    const gapsContainer = document.getElementById('modalGapsContainer');
    gapsContainer.innerHTML = c.gaps.length > 0 
      ? c.gaps.map(g => `<span class="pill pill-gap">${escapeHtml(g)}</span>`).join('')
      : '<span style="font-size:0.85rem; color:var(--text-muted);">No critical skill gaps found</span>';

    const qList = document.getElementById('modalQuestionsList');
    qList.innerHTML = c.interview_questions.length > 0 
      ? c.interview_questions.map(q => `<li>${escapeHtml(q)}</li>`).join('')
      : '<li>Ask general software architecture and past experience questions.</li>';

    candidateModal.classList.remove('hidden');
  }

  function closeModal() {
    candidateModal.classList.add('hidden');
  }

  function escapeHtml(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }
});
