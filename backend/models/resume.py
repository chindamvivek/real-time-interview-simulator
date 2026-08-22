from pydantic import BaseModel
from typing import Optional


class Project(BaseModel):
    name: str
    description: Optional[str] = None
    technologies: list[str] = []


class WorkExperience(BaseModel):
    company: str
    role: str
    duration: Optional[str] = None
    responsibilities: list[str] = []


class Education(BaseModel):
    institution: str
    degree: str
    year: Optional[str] = None


class ResumeData(BaseModel):
    """
    Structured representation of a parsed resume.
    This is what the LLM will return as JSON after reading the raw text.
    """
    name: Optional[str] = None
    summary: Optional[str] = None
    skills: list[str] = []
    work_experience: list[WorkExperience] = []
    projects: list[Project] = []
    education: list[Education] = []
    certifications: list[str] = []
