import docx
import re
import pdfplumber

def parse_resume(file_name: str):
    result = []
    if file_name.lower().endswith(".pdf"):
        with pdfplumber.open(file_name) as pdf:
            for page in pdf.pages:
                if page.extract_text() is not None:
                    result.append(page.extract_text(x_tolerance=2))
        return "\n".join(result)
    elif file_name.lower().endswith(".docx"):
        lines = docx.Document(file_name)
        for paragraph in lines.paragraphs:
            if paragraph.text is not None:
                result += paragraph.text + '\n'
        return result
    else:
        raise ValueError("Unsupported file type")

def remove_contact_info(text: str):
    # Remove email addresses
    text = re.sub(
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b',
        '',
        text
    )
    # Remove phone numbers
    text = re.sub(
        r'(?<!\d)(?:\+?\d[\d\s().-]{8,}\d)(?!\d)',
        '',
        text
    )
    #remove special characters
    text = text.encode("ascii", "ignore").decode()

    return text