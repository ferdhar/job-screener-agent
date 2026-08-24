from dataclasses import dataclass
from typing import Optional

from app.models import JobPosting, ResumeMatch


@dataclass
class AgentState:
    job_url: str
    resume_text: str

    job_text: Optional[str] = None
    job: Optional[JobPosting] = None
    match: Optional[ResumeMatch] = None
    score: Optional[dict] = None
