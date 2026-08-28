import io
from fastapi import APIRouter, HTTPException, File, Form, UploadFile
from backend.config import MAX_FILE_SIZE_MB
from backend.services.resume_parser import parse_resume_to_json
from backend.services.session_manager import create_session

router = APIRouter()

@router.post("/resume/upload")
async def upload_resume(
    file: UploadFile = File(...),
    job_role: str = Form(...),
    job_description: str = Form("")
    ):
    allowed_types = [
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code = 400,  
            detail="Only PDF and DOCX files are allowed"
        )

    file_bytes = await file.read()

    if len(file_bytes) > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail=f"File size must be less than {MAX_FILE_SIZE_MB} MB"
        )

    file_stream = io.BytesIO(file_bytes)
    parsed_resume = parse_resume_to_json(file_stream, file.filename)
    session_id = create_session(parsed_resume, job_role, job_description)

    return {
        "session_id": session_id,
        "resume_data": parsed_resume.model_dump()
    }