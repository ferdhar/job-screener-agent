from typing import Optional, TypedDict

from app.models import JobPosting, ResumeMatch


class ApplicationAgentState(TypedDict, total=False):
    job: Optional[JobPosting]
    resume_text: str
    match: Optional[ResumeMatch]
    score: Optional[dict]

    analysis: Optional[dict]

    candidate_evidence: Optional[list[str]]
    company_research: list[str]

    draft: Optional[str]
    cover_letter: Optional[str]
    critique: Optional[str]

    revision_count: int

    error: Optional[str]