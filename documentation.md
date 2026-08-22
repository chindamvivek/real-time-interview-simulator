# Project Documentation — Real-Time AI Interview Simulator

---

## Session: 2026-08-22

### What Was Decided and Why

| Decision | Reasoning |
|----------|-----------|
| Python + FastAPI for backend | Fast to build, async-capable, great for WebSocket & REST, easy to deploy |
| Next.js for frontend | React-based, SSR-ready, file-based routing simplifies multi-page setup |
| Google Gemini LLM | User already has Gemini API key; `google-genai` is the current unified SDK |
| Guest sessions (no auth in v1) | Avoids complexity early; can layer Auth (Supabase/Firebase) in v2 |
| Browser Web Speech API for TTS/STT | Zero latency, no API cost, works offline; upgrade path to ElevenLabs in v2 |
| In-memory session storage | Simplest working solution; swap to Redis in v2 with minimal refactor |
| PII redaction before LLM call | Privacy-by-design: strip phone/email/address before any LLM sees the resume |

### Build Order
Following a collaborative protocol where **I (AI) build a feature → user reviews it → user builds next feature → repeat**.

---

### What Was Built

#### By AI (Session 1)
- `backend/config.py` — App-wide configuration loaded from `.env` via `python-dotenv`. Includes `validate_config()` to catch missing API keys at startup.
- `backend/models/resume.py` — Pydantic models: `ResumeData`, `WorkExperience`, `Project`, `Education`. This is the structured JSON schema the LLM will produce.
- `backend/requirements.txt` — All backend dependencies pinned by name.
- `backend/.env.example` — Template for environment variables (safe to commit, actual `.env` must be gitignored).

#### By User (Session 1)
- `backend/services/resume_parser.py` — Initial text extraction from PDF (pdfplumber) and DOCX (python-docx), plus a `remove_contact_info()` function using regex.

**Code review of user's `resume_parser.py`:**
- ✅ Correct use of `.lower().endswith()` for file extension checking
- ✅ Good separation of concerns (extract vs. redact are separate functions)
- 🐛 `import re` is missing — `remove_contact_info` will crash
- 🐛 `pdfplumber.page.extract_text()` can return `None` on scanned PDFs — needs a guard
- 🐛 `parse_resume` returns `None` for unsupported file types instead of raising an error
- ❌ `result += string` in a loop — use list + `join` instead (more Pythonic)
- ❌ DOCX block has inconsistent indentation

---

### Current State / Where We Left Off

**Backend — In Progress**
- [x] `.venv` created, all packages installed
- [x] `services/resume_parser.py` — user-written, needs bug fixes (see review above)
- [x] `config.py` — done
- [x] `models/resume.py` — done
- [x] `requirements.txt` — done
- [x] `.env.example` — done
- [ ] `services/resume_parser.py` — user's next task: fix bugs from review
- [ ] `services/session_manager.py`
- [ ] `services/interview_engine.py`
- [ ] `services/feedback_generator.py`
- [ ] `routers/resume.py`
- [ ] `routers/interview.py`
- [ ] `routers/websocket.py`
- [ ] `main.py`

**Frontend** — Not started yet

**Git** — Initialized, `.gitignore` created and populated.

---

## Git — When to Initialize

Initialize Git right now (or after the user fixes `resume_parser.py`), before writing any more code.

### Exact steps:

```bash
# 1. From the project root (real time interview/)
git init

# 2. Create .gitignore FIRST before staging anything

# 3. Stage and commit the current foundation
git add .
git commit -m "feat: initial backend foundation (config, models, requirements)"

# 4. Connect to GitHub (create a repo on github.com first, then:)
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git branch -M main
git push -u origin main
```

### .gitignore content for this project:
```
# Python
__pycache__/
*.py[cod]
.venv/
*.egg-info/

# Environment secrets — NEVER commit this
.env

# OS
.DS_Store
Thumbs.db

# Node (frontend, later)
node_modules/
.next/
```

---
