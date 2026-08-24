import json

from app.scraper import fetch_job_posting
from app.extractor import extract_job_posting
from app.matcher import match_resume_to_job
from app.scorer import calculate_fit_score

def fetch_job(url: str) -> str:
    """
    Fetch a job posting from a URL.
    """
    return fetch_job_posting(url)


def extract_job(job_text: str) -> dict:
    """
    Extract structured information from raw job-posting text.
    """
    job = extract_job_posting(job_text)

    return job.model_dump()


def match_resume(resume_text: str, job_data: dict) -> dict:
    """
    Match a resume against structured job requirements.
    """
    from app.models import JobPosting

    job = JobPosting.model_validate(job_data)

    match = match_resume_to_job(
        resume_text=resume_text,
        job=job,
    )

    return match.model_dump()


def calculate_score(match_data: dict, job_data: dict) -> dict:
    """
    Calculate the candidate's fit score.
    """
    from app.models import JobPosting, ResumeMatch

    job = JobPosting.model_validate(job_data)
    match = ResumeMatch.model_validate(match_data)

    return calculate_fit_score(
        job=job,
        match=match,
    )

TOOL_FUNCTIONS = {
    "fetch_job": fetch_job,
    "extract_job": extract_job,
    "match_resume": match_resume,
    "calculate_score": calculate_score,
}
