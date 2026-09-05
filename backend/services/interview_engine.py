from google import genai
from google.genai import types

from backend.config import GEMINI_API_KEY, GEMINI_MODEL
from backend.services.session_manager import get_session, add_message


def build_system_prompt(session: dict) -> str:
    """
    Builds the AI interviewer's system instruction using the candidate's
    parsed resume, target job role, and job description from the session.

    This is what gives the AI its "personality" and context for the interview.
    """
    job_role = session.get("job_role", "Software Engineer")
    job_description = session.get("job_description", "")
    resume = session.get("resume_data")

    # --- Extract resume fields safely ---
    candidate_name = getattr(resume, "candidate_name", None) or "Candidate"

    skills = ", ".join(getattr(resume, "skills", []) or []) or "Not listed"

    # Format each project into a readable line
    projects_list = getattr(resume, "projects", []) or []
    projects_summary = "\n".join([
        f"  - {p.name}: {p.description or 'No description'} "
        f"(Technologies: {', '.join(p.technologies) if p.technologies else 'Not specified'})"
        for p in projects_list
    ]) if projects_list else "  None listed"

    # Format each experience entry into a readable line
    exp_list = getattr(resume, "experience", []) or []
    exp_summary = "\n".join([
        f"  - {e.role} at {e.company} "
        f"({e.start_date or 'Unknown'} - {e.end_date or 'Present'}): "
        f"{e.description or 'No details provided'}"
        for e in exp_list
    ]) if exp_list else "  None listed"

    # Format certifications as a comma-separated list
    certifications = getattr(resume, "certifications", []) or []
    certifications_summary = ", ".join(certifications) if certifications else "None listed"

    # Format achievements as a comma-separated list
    achievements = getattr(resume, "achievements", []) or []
    achievements_summary = ", ".join(achievements) if achievements else "None listed"

    return f"""
You are a professional technical interviewer named Alex at a top technology company.
You are conducting a realistic, conversational interview for the role of **{job_role}**.

CANDIDATE PROFILE:
- Name: {candidate_name}
- Skills: {skills}
- Certifications: {certifications_summary}
- Achievements: {achievements_summary}

WORK EXPERIENCE:
{exp_summary}

PROJECTS:
{projects_summary}

JOB REQUIREMENTS:
{job_description if job_description else f"Standard industry expectations for a {job_role} role."}

INTERVIEW RULES (follow these strictly):
1. Speak directly to the candidate — natural, professional tone.
2. Ask ONLY ONE question at a time. Keep it to 1-3 sentences max.
3. Base questions on the candidate's actual resume, skills, job requirements, certifications, and achievements above.
4. If their previous answer was brief or vague, ask a relevant follow-up before moving on.
5. Do NOT repeat greetings or re-introduce yourself after the first message.
6. Do NOT output lists, bullet points, or markdown. Plain conversational text only.
7. After 8-10 exchanges, wrap up the interview professionally.
"""


def generate_next_question(session_id: str, user_response: str = None) -> str:
    """
    Core interview engine function. Called every time the user finishes speaking.

    Flow:
        1. Validate the session exists
        2. Save the user's latest answer to conversation history (if provided)
        3. Build the system prompt from resume + job context
        4. Format the full conversation history into Gemini's expected format
        5. *** YOUR TASK: Call Gemini API and get the next question ***
        6. *** YOUR TASK: Save the AI question to history and return it ***

    Args:
        session_id:    The active session UUID.
        user_response: The candidate's spoken/typed answer (None at interview start).

    Returns:
        The next interview question as a plain string.
    """
    # Step 1: Get the session — raise an error if it doesn't exist
    session = get_session(session_id)
    if not session:
        raise ValueError(f"Session '{session_id}' not found or has expired.")

    # Step 2: If the user said something, save it to conversation history
    if user_response and user_response.strip():
        add_message(session_id, "user", user_response.strip())

    # Step 3: Build the system prompt from the session's resume + job context
    system_prompt = build_system_prompt(session)

    # Step 4: Format conversation history into Gemini's Content format
    # Gemini expects a list of Content objects, each with a "role" and "parts".
    # Our roles are "ai" and "user" — but Gemini expects "model" (not "ai") and "user".
    contents = []
    history = session.get("conversation_history", [])

    for msg in history:
        gemini_role = "model" if msg["role"] == "ai" else "user"
        contents.append(
            types.Content(
                role=gemini_role,
                parts=[types.Part.from_text(text=msg["content"])],
            )
        )

    # If no history yet, this is the very first message — prompt the AI to start
    if not contents:
        contents.append(
            types.Content(
                role="user",
                parts=[types.Part.from_text(
                    text=(
                        "Begin the interview now. "
                        "Greet the candidate warmly and briefly introduce yourself as their interviewer. "
                        "Then ask them to tell you about themselves and their background — "
                        "keep it simple, friendly, and professional. One short question only."
                    )
                )],
            )
        )

    # -------------------------------------------------------------------------
    # YOUR TASK — Steps 5 & 6
    # -------------------------------------------------------------------------
    # Step 5: Create a Gemini client and call generate_content.
    #   - Use `genai.Client(api_key=GEMINI_API_KEY)` to create the client
    #   - Call `client.models.generate_content(...)` with:
    #       model   = GEMINI_MODEL
    #       contents = contents  (the list we just built above)
    #       config  = types.GenerateContentConfig(
    #                     system_instruction = system_prompt,
    #                     temperature        = 0.7   (higher than parser — more natural)
    #                 )
    #
    # Step 6: Extract the AI's response text, save it to history, then return it.
    #   - Get the question text from response.text and strip whitespace
    #   - Call add_message(session_id, "ai", ai_question) to save it
    #   - Return the ai_question string
    #
    # Hint: Look at how parse_resume_to_json() in resume_parser.py calls Gemini —
    # the pattern is almost identical, just without response_schema this time.
    # -------------------------------------------------------------------------

    client = genai.Client(api_key=GEMINI_API_KEY)
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.7,
        )
    )

    #adding ai response to conversation history
    add_message(session_id, "ai", response.text.strip())
    return response.text.strip()

    