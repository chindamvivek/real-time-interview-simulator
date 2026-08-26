from pydantic import BaseModel
from google import genai
from google.genai import types
from backend.config import GEMINI_API_KEY, GEMINI_MODEL
from backend.services.session_manager import get_session


class QuestionFeedback(BaseModel):
    question: str
    user_answer: str
    feedback: str
    score: int


class FeedbackReport(BaseModel):
    overall_score: int
    communication_score: int
    technical_score: int
    strengths: list[str]
    areas_to_improve: list[str]
    question_breakdown: list[QuestionFeedback] #per question analysis
    summary: str

def generate_feedback(session_id: str) -> FeedbackReport:
    session = get_session(session_id)
    if not session:
        raise ValueError("session not found or expired")

    history = session["conversation_history"]
    if not history:
        raise ValueError("interview did not happend")
    
    text_history = ""

    for msg in history:
        text_history += f"{'Interviewer' if msg['role'] == 'ai' else 'Candidate'}: {msg.get('content')}\n"
    job_role = session.get("job_role")
    job_description = session.get("job_description")

    user_prompt = f"""
    You are an expert interview coach analyzing a completed mock interview.

    ROLE APPLIED FOR: {job_role}

    JOB DESCRIPTION:
    {job_description if job_description else f"Standard industry expectations for a {job_role} role."}

    INTERVIEW TRANSCRIPT:
    {text_history}

    Analyze the candidate's performance across all questions.
    Be honest, specific, and constructive in your evaluation.
    Judge scores relative to the expectations for the role above.
    """
    client = genai.Client(api_key=GEMINI_API_KEY)
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=user_prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=FeedbackReport,
            temperature=0.2,
        ),
    )
    # Return parsed Pydantic model with fallback
    if response.parsed:
        return response.parsed
    return FeedbackReport.model_validate_json(response.text)



