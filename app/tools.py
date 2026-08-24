from app.scraper import fetch_job_posting
from app.extractor import extract_job_posting
from app.matcher import match_resume_to_job
from app.scorer import calculate_fit_score
from app.state import AgentState


def fetch_job(state: AgentState) -> str:
    """
    Fetch the job posting and store the raw text in agent state.
    """

    state.job_text = fetch_job_posting(state.job_url)

    return state.job_text


def extract_job(state: AgentState) -> dict:
    """
    Extract structured job information and store it in agent state.
    """

    if state.job_text is None:
        raise RuntimeError(
            "Cannot extract job because job_text is not available."
        )

    state.job = extract_job_posting(state.job_text)

    return state.job.model_dump()


def match_resume(state: AgentState) -> dict:
    """
    Match the resume against the job stored in agent state.
    """

    if state.job is None:
        raise RuntimeError(
            "Cannot match resume because job data is not available."
        )

    state.match = match_resume_to_job(
        resume_text=state.resume_text,
        job=state.job,
    )

    return state.match.model_dump()


def calculate_score(state: AgentState) -> dict:
    """
    Calculate the fit score using the job and resume match
    stored in agent state.
    """

    if state.job is None:
        raise RuntimeError(
            "Cannot calculate score because job data is not available."
        )

    if state.match is None:
        raise RuntimeError(
            "Cannot calculate score because resume match is not available."
        )

    state.score = calculate_fit_score(
        job=state.job,
        match=state.match,
    )

    return state.score


TOOL_FUNCTIONS = {
    "fetch_job": fetch_job,
    "extract_job": extract_job,
    "match_resume": match_resume,
    "calculate_score": calculate_score,
}