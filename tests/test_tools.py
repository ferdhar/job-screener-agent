from unittest.mock import patch

from app.state import AgentState
from app.tools import fetch_job, extract_job
from app.models import JobPosting


def make_state():
    return AgentState(
        job_url="https://example.com/job",
        resume_text="Some resume text",
    )


@patch("app.tools.fetch_job_posting")
def test_fetch_job_populates_state_from_job_url(mock_fetch):
    mock_fetch.return_value = "raw job text"

    state = make_state()
    result = fetch_job(state)

    mock_fetch.assert_called_once_with(state.job_url)
    assert result["ok"] is True
    assert result["data"] == "raw job text"
    assert state.job_text == "raw job text"


@patch("app.tools.fetch_job_posting")
def test_fetch_job_returns_error_on_failure(mock_fetch):
    mock_fetch.side_effect = RuntimeError("boom")

    state = make_state()
    result = fetch_job(state)

    assert result["ok"] is False
    assert result["error"]["retryable"] is True
    assert state.job_text is None


def test_extract_job_returns_error_when_job_text_missing():
    state = make_state()

    result = extract_job(state)

    assert result["ok"] is False
    assert result["error"]["type"] == "MissingJobText"
    assert state.job is None


@patch("app.tools.extract_job_posting")
def test_extract_job_populates_state_from_job_text(mock_extract):
    job = JobPosting(
        title="Engineer",
        company="Acme",
        location="Remote",
        responsibilities=[],
        requirements=[],
        technical_skills=[],
    )
    mock_extract.return_value = job

    state = make_state()
    state.job_text = "raw job text"

    result = extract_job(state)

    mock_extract.assert_called_once_with("raw job text")
    assert result["ok"] is True
    assert result["data"] == job.model_dump()
    assert state.job == job
