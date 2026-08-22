from pydantic import BaseModel
from typing import Optional


class Education(BaseModel):
    degree: Optional[str] = None
    field: Optional[str] = None
    institution: Optional[str] = None
    start_year: Optional[int] = None
    end_year: Optional[int] = None
    cgpa: Optional[float] = None


class Project(BaseModel):
    name: str
    description: Optional[str] = None
    technologies: list[str] = []


class Experience(BaseModel):
    company: str
    role: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = None


class ResumeData(BaseModel):
    """
    Structured representation of a parsed resume.
    This is what the LLM will return as JSON after reading the raw text.
    """
    candidate_name: Optional[str] = None
    education: list[Education] = []
    skills: list[str] = []
    projects: list[Project] = []
    experience: list[Experience] = []
    certifications: list[str] = []
    achievements: list[str] = []
