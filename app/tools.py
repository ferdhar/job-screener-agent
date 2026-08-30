from app.scraper import fetch_job_posting
from app.extractor import extract_job_posting
from app.matcher import match_resume_to_job
from app.scorer import calculate_fit_score
from app.state import AgentState


def fetch_job(state: AgentState) -> str:
    """
    Fetch the job posting and store the raw text in agent state.
    """
    try:
        result = fetch_job_posting(state.job_url)
        state.job_text = result

        return tool_success(result)

    except Exception as exc:
        return tool_error(
            error_type=type(exc).__name__,
            message=str(exc),
            retryable=True,
        )


def extract_job(state: AgentState) -> dict:
    """
    Extract structured job information and store it in agent state.
    """
    if state.job_text is None:
        return tool_error(
            error_type="MissingJobText",
            message="Cannot extract job because job_text is not available.",
            retryable=False,
        )

    try:
        job = extract_job_posting(state.job_text)
        state.job = job

        return tool_success(job.model_dump())

    except Exception as exc:
        return tool_error(
            error_type=type(exc).__name__,
            message=str(exc),
            retryable=False,
        )


def match_resume(state: AgentState) -> dict:
    """
    Match the resume against the job stored in agent state.
    """

    if state.job is None:
        return tool_error(
            error_type="MissingJobData",
            message="Cannot match resume because job data is not available.",
            retryable=False,
        )

    try:
        state.match = match_resume_to_job(
            resume_text=state.resume_text,
            job=state.job,
        )

        return tool_success(
            state.match.model_dump()
        )

    except Exception as exc:
        return tool_error(
            error_type=type(exc).__name__,
            message=f"Failed to match resume: {exc}",
            retryable=True,
        )


def calculate_score(state: AgentState) -> dict:
    """
    Calculate the fit score using the job and resume match
    stored in agent state.
    """

    if state.job is None:
        return tool_error(
            error_type="MissingJobData",
            message="Cannot calculate score because job data is not available.",
            retryable=False,
        )

    if state.match is None:
        return tool_error(
            error_type="MissingResumeMatch",
            message="Cannot calculate score because resume match is not available.",
            retryable=False,
        )

    try:
        state.score = calculate_fit_score(
            job=state.job,
            match=state.match,
        )

        return tool_success(
            state.score
        )

    except Exception as exc:
        return tool_error(
            error_type=type(exc).__name__,
            message=f"Failed to calculate score: {exc}",
            retryable=False,
        )


def tool_success(data):
    return {
        "ok": True,
        "data": data,
        "error": None,
    }


def tool_error(error_type, message, retryable=False):
    return {
        "ok": False,
        "data": None,
        "error": {
            "type": error_type,
            "message": message,
            "retryable": retryable,
        },
    }

TOOL_FUNCTIONS = {
    "fetch_job": fetch_job,
    "extract_job": extract_job,
    "match_resume": match_resume,
    "calculate_score": calculate_score,
}