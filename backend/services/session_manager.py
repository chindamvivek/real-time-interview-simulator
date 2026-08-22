import uuid
from datetime import datetime
from backend.models.resume import ResumeData

# In-memory store: { session_id -> session_dict }
# v1 uses a plain dict (fast, simple). In v2, this swaps to Redis for persistence.
sessions = {}


def create_session(resume_data: ResumeData, job_role: str, job_description: str = "") -> str:
    """
    Creates a new interview session and stores it in memory.

    Args:
        resume_data:      Parsed resume as a ResumeData Pydantic object.
        job_role:         Job title the user is applying for (e.g. "Software Engineer").
        job_description:  Full job posting text (optional but improves AI question quality).

    Returns:
        session_id (str): A unique UUID string used to reference this session later.
    """
    session_id = str(uuid.uuid4())
    sessions[session_id] = {
        "session_id": session_id,
        "resume_data": resume_data,
        "job_role": job_role,
        "job_description": job_description,
        "conversation_history": [],
        "created_at": datetime.now(),
    }
    return session_id  # Return only the ID — the caller uses this to look up the session


def get_session(session_id: str) -> dict | None:
    """
    Retrieves a session by ID.
    Returns None if the session doesn't exist (e.g. expired or invalid ID).
    """
    return sessions.get(session_id)


def add_message(session_id: str, role: str, content: str) -> None:
    """
    Appends a message to a session's conversation history.

    Args:
        session_id: The session to update.
        role:       Who sent the message — "ai" (interviewer) or "user" (candidate).
        content:    The actual text of the message.

    Example conversation_history after 2 exchanges:
        [
            {"role": "ai",   "content": "Tell me about yourself."},
            {"role": "user", "content": "I have 2 years of Python experience..."},
        ]
    """
    session = get_session(session_id)
    if session:
        session["conversation_history"].append({"role": role, "content": content})