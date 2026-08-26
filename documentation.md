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
| `job_description` added to session | Richer context enables role-specific questions beyond just job title |
| Certifications & achievements in prompt | All resume fields should reach the interviewer for maximum interview depth |
| Opening question fixed to "tell me about yourself" | Ensures a natural, consistent interview start experience for every user |

### Build Protocol
Collaborative — **AI builds a feature → User reviews it → User builds next feature → AI reviews → repeat.**

---

## Session 1 (2026-08-22) — Foundation Setup

### By AI
- `backend/config.py` — App-wide settings from `.env`. `validate_config()` guards missing API key at startup.
- `backend/models/resume.py` — Pydantic schema (initial version with `WorkExperience`, `Project`, `Education`, `ResumeData`).
- `backend/requirements.txt` — All backend dependencies.
- `backend/.env.example` — Safe commit-able template (later removed from tracking).

### By User
- `backend/services/resume_parser.py` — Initial attempt: PDF/DOCX text extraction + PII regex redaction.
- `.gitignore`, Git repo initialization, first commit, GitHub push.

**Code Review of User's `resume_parser.py` (Session 1 attempt):**
- ✅ Correct `.lower().endswith()`, good separation of extract vs. redact functions
- 🐛 `import re` missing — crash on `remove_contact_info()`
- 🐛 `page.extract_text()` can return `None` — no guard
- 🐛 Returns `None` for unsupported types instead of raising `ValueError`
- ❌ DOCX: `result += string` on a list — appends individual characters, not full strings
- ❌ Inconsistent indentation in DOCX block

---

## Session 2 (2026-08-22) — Resume Parser & Schema Merge

### Schema Merge Decision
User's original inline schema (written before the project started) was richer than AI's initial `models/resume.py`. **Best of both merged:**
- Kept AI's design: schema in a separate `models/resume.py` file (not inline in the parser)
- Kept User's fields: `start_year`/`end_year` as `int`, `cgpa` as `float`, separate `start_date`/`end_date` on `Experience`, `achievements: list[str]`

### Final `models/resume.py` Schema
```
Education:    degree, field, institution, start_year (int), end_year (int), cgpa (float)
Project:      name, description, technologies (list)
Experience:   company, role, start_date, end_date, description
ResumeData:   candidate_name, education, skills, projects, experience, certifications, achievements
```

### Final `resume_parser.py` Functions
- `extract_raw_text(file_path)` — Safe PDF/DOCX extraction (None guard, list+join, empty-line filter, ValueError for bad types)
- `remove_contact_info(text)` — Regex redaction with `[REDACTED_EMAIL]` / `[REDACTED_PHONE]` placeholders
- `parse_resume_to_json(file_path)` — Full pipeline: extract → redact → Gemini with `response_schema=ResumeData` → validated Pydantic object

**Gemini call pattern:**
- XML tags `<resume_text>...</resume_text>` to clearly mark content boundaries (from user's version)
- Separate `system_instruction` parameter (from user's version — correct Gemini design)
- `temperature=0.1` for precise factual extraction
- Fallback: `ResumeData.model_validate_json(response.text)` if `response.parsed` is empty

### By User
- `backend/services/session_manager.py` — In-memory session management.
- Git commits and GitHub push (`https://github.com/chindamvivek/real-time-interview-simulator`)

**Code Review of User's `session_manager.py`:**
- ✅ Correct `uuid.uuid4()`, `datetime.now()`, `sessions.get()` usage
- ✅ `add_message()` logic correct
- 🐛 `create_session()` returned `sessions[session_id]` (the whole dict) instead of `session_id` (the string) — fixed
- 💡 `job_description` parameter was missing — added in fix

### Final `session_manager.py` Functions
- `create_session(resume_data, job_role, job_description)` → returns `session_id` string
- `get_session(session_id)` → returns session dict or `None`
- `add_message(session_id, role, content)` → appends `{"role": role, "content": content}` to `conversation_history`

---

## Session 3 (2026-08-25 & 2026-08-26) — Interview Engine

### By AI (skeleton + Steps 1-4)
- `backend/services/interview_engine.py` — Created scaffold with `build_system_prompt()` complete and Steps 1-4 of `generate_next_question()` complete. Left Steps 5-6 (Gemini call + response save) for user.

### By User (Steps 5-6 implemented correctly)
```python
client = genai.Client(api_key=GEMINI_API_KEY)
response = client.models.generate_content(
    model=GEMINI_MODEL,
    contents=contents,
    config=types.GenerateContentConfig(system_instruction=system_prompt, temperature=0.7)
)
add_message(session_id, "ai", response.text.strip())
return response.text.strip()
```
✅ Correct pattern, correct config, correct save. No bugs.

### Key Decisions in `interview_engine.py`
| Decision | Reason |
|---|---|
| `system_instruction` separate from contents | Gemini re-reads it before every response — keeps AI in character |
| `temperature=0.7` | Higher than parser (0.1) — natural conversation variation, not robotic |
| Conversation history replayed on every call | Gemini is stateless; history must be sent every time |
| `"model"` not `"ai"` in Gemini role field | API requirement — our internal storage uses "ai", translated before API call |
| First trigger message set to "tell me about yourself" style | Consistent, warm interview opening for all candidates |
| Certifications and achievements added to system prompt | All resume fields should be visible to the interviewer AI |

### Final `interview_engine.py` Functions
- `build_system_prompt(session)` → formats resume + job context into a system instruction string
- `generate_next_question(session_id, user_response=None)` → full conversation loop: save answer → build prompt → format history → call Gemini → save response → return question

---

## Current State / Where We Left Off

**Backend — In Progress**
- [x] `config.py` — done
- [x] `models/resume.py` — done
- [x] `requirements.txt` — done
- [x] `services/resume_parser.py` — done
- [x] `services/session_manager.py` — done
- [x] `services/interview_engine.py` — done
- [ ] `services/feedback_generator.py` ← **USER'S NEXT TASK**
- [ ] `routers/resume.py`
- [ ] `routers/interview.py`
- [ ] `routers/websocket.py`
- [ ] `main.py`

**Frontend** — Not started yet

**Git** — Connected to GitHub. Repo: `https://github.com/chindamvivek/real-time-interview-simulator`

---
