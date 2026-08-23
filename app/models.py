from pydantic import BaseModel
from typing import Literal


class Requirement(BaseModel):
    description: str
    category: Literal[
        "education",
        "experience",
        "technical_skill",
        "domain_knowledge",
        "responsibility",
        "communication",
        "other",
    ]
    importance: Literal[
        "required",
        "preferred",
    ]


class JobPosting(BaseModel):
    title: str
    company: str
    location: str
    responsibilities: list[str]
    requirements: list[Requirement]
    technical_skills: list[str]


class RequirementMatch(BaseModel):
    requirement: str
    status: Literal[
        "matched",
        "partial",
        "missing",
    ]
    evidence: str


class ResumeMatch(BaseModel):
    requirement_matches: list[RequirementMatch]
    strengths: list[str]
    gaps: list[str]
