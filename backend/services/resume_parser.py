import re
import docx
import pdfplumber
from google import genai
from google.genai import types

from backend.config import GEMINI_API_KEY, GEMINI_MODEL
from backend.models.resume import ResumeData


def extract_raw_text(file_path: str) -> str:
    """
    Extracts raw text from a PDF or DOCX file.
    Raises ValueError for unsupported file types or unreadable files.
    """
    file_path_lower = file_path.lower()

    if file_path_lower.endswith(".pdf"):
        pages_text = []
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text(x_tolerance=2)
                if text:  # guard: extract_text() returns None on scanned/image PDFs
                    pages_text.append(text)
        return "\n".join(pages_text)

    elif file_path_lower.endswith(".docx"):
        doc = docx.Document(file_path)
        paragraphs_text = [
            p.text for p in doc.paragraphs if p.text and p.text.strip()
        ]
        return "\n".join(paragraphs_text)

    else:
        raise ValueError(
            f"Unsupported file type for '{file_path}'. Only .pdf and .docx are supported."
        )


def remove_contact_info(text: str) -> str:
    """
    Redacts PII (email addresses, phone numbers) from raw resume text
    before sending to LLM. Replaces with placeholders to preserve sentence structure.
    """
    # Remove email addresses
    text = re.sub(
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b',
        '[REDACTED_EMAIL]',
        text
    )
    # Remove phone numbers (handles international formats)
    text = re.sub(
        r'(?<!\d)(?:\+?\d[\d\s().-]{8,}\d)(?!\d)',
        '[REDACTED_PHONE]',
        text
    )
    # Strip non-ASCII characters (handles unicode artifacts from PDF extraction)
    text = text.encode("ascii", "ignore").decode()

    return text


def parse_resume_to_json(file_path: str) -> ResumeData:
    """
    Full parsing pipeline:
    1. Extract raw text from file (PDF/DOCX)
    2. Redact PII contact info
    3. Call Gemini with system_instruction + structured response_schema
    4. Return validated ResumeData Pydantic instance with fallback
    """
    # Step 1: Extract text
    raw_text = extract_raw_text(file_path)
    if not raw_text.strip():
        raise ValueError("The uploaded document contains no readable text.")

    # Step 2: Redact PII
    sanitized_text = remove_contact_info(raw_text)

    # Step 3: Call Gemini with structured JSON output
    client = genai.Client(api_key=GEMINI_API_KEY)

    # Wrap resume text in XML-like tags to clearly mark context boundaries for the LLM
    user_prompt = f"""
    Extract the structured resume data from the text below:

    <resume_text>
    {sanitized_text}
    </resume_text>
    """

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=user_prompt,
        config=types.GenerateContentConfig(
            # system_instruction keeps rules clearly separate from resume content
            system_instruction=(
                "You are an expert HR data parser. Extract candidate information accurately "
                "from the provided resume text into the requested structure. "
                "Do not invent information that is not present in the text."
            ),
            response_mime_type="application/json",
            response_schema=ResumeData,
            temperature=0.1,  # low temperature: factual extraction, not creative generation
        ),
    )

    # Step 4: Return parsed Pydantic model (with fallback)
    if response.parsed:
        return response.parsed
    else:
        # Fallback: manually parse the raw JSON text if response.parsed is empty
        return ResumeData.model_validate_json(response.text)