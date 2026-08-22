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

#### By User (Session 1 & 2)
- Initial attempt at `backend/services/resume_parser.py` (PDF and DOCX parsing + PII regex).
- Git repository initialization and initial commit.

**Code Review of User's `resume_parser.py` Attempt:**
- ✅ **Good:** Added `import re`, added `if page.extract_text() is not None:`, added `raise ValueError("Unsupported file type")`, used `"\n".join(result)` for PDFs.
- 🐛 **Bug Identified:** In the `.docx` branch, `result` (initialized as a `list`) was mutated with string concatenation `result += paragraph.text + '\n'`. In Python, adding a string to a list appends each character as an item, returning a list of single characters rather than a string!
- 💡 **Best Practice:** Use list comprehensions for cleaner paragraph filtering: `[p.text for p in doc.paragraphs if p.text and p.text.strip()]`.

#### By AI (Session 2 — Feature 2)
- Refactored `backend/services/resume_parser.py`:
  - `extract_raw_text(file_path)`: Fixed list vs string bug in DOCX, cleaned up text extraction for PDF and DOCX.
  - `remove_contact_info(text)`: Replaced regex matches with explicit `[REDACTED_EMAIL]` and `[REDACTED_PHONE]` tags instead of blank spaces.
  - `parse_resume_to_json(file_path)`: Integrated `google-genai` SDK with `response_schema=ResumeData` to directly return validated Pydantic object parsed from resume text via Gemini LLM.

---

### Current State / Where We Left Off

**Backend — In Progress**
- [x] `.venv` created, packages installed
- [x] `.gitignore` populated, Git repository initialized & committed
- [x] `config.py` — done
- [x] `models/resume.py` — done
- [x] `requirements.txt` & `.env.example` — done
- [x] `services/resume_parser.py` — completed (extract + redact PII + Gemini structured extraction)
- [ ] `services/session_manager.py` — user's next task!
- [ ] `services/interview_engine.py`
- [ ] `services/feedback_generator.py`
- [ ] `routers/resume.py`
- [ ] `routers/interview.py`
- [ ] `routers/websocket.py`
- [ ] `main.py`

**Frontend** — Not started yet

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
