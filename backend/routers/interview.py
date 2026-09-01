from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.services.session_manager import get_session
from backend.services.interview_engine import generate_next_question
from backend.services.feedback_generator import generate_feedback, FeedbackReport

router = APIRouter()


# --- Request body schemas ---

class StartRequest(BaseModel):
    session_id: str


class AnswerRequest(BaseModel):
    session_id: str
    user_response: str


# --- Endpoints ---

@router.post("/interview/start")
def start_interview(request: StartRequest):
    """
    Called once when the user clicks "Start Interview".
    Triggers the AI to generate the opening question (no user answer yet).
    """
    session = get_session(request.session_id)
    if not session:
        raise HTTPException(
            status_code=404,
            detail=f"Session '{request.session_id}' not found or has expired."
        )

    question = generate_next_question(request.session_id)
    return {"question": question}


@router.post("/interview/answer")
def submit_answer(request: AnswerRequest):
    """
    Called every time the user finishes speaking their answer.
    Saves the user's response and returns the next AI question.
    """
    session = get_session(request.session_id)
    if not session:
        raise HTTPException(
            status_code=404,
            detail=f"Session '{request.session_id}' not found or has expired."
        )

    question = generate_next_question(request.session_id, request.user_response)
    return {"question": question}


@router.post("/interview/feedback")
def get_feedback(request: StartRequest) -> FeedbackReport:
    """
    Called when the interview ends.
    Analyzes the full conversation history and returns a structured feedback report.
    """
    session = get_session(request.session_id)
    if not session:
        raise HTTPException(
            status_code=404,
            detail=f"Session '{request.session_id}' not found or has expired."
        )

    feedback_report = generate_feedback(request.session_id)
    return feedback_report
