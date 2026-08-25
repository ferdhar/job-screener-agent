from typing import TypedDict

from langgraph.graph import StateGraph, START, END

from app.scraper import fetch_job_posting
from app.extractor import extract_job_posting
from app.matcher import match_resume_to_job
from app.scorer import calculate_fit_score


class AgentState(TypedDict, total=False):
    job_url: str
    resume_text: str

    job_text: str
    job: object
    match: object
    score: dict

    error: str
    error_count: int


def fetch_job(state: AgentState) -> AgentState:
    """
    Fetch the job posting from the URL.
    """

    try:
        job_text = fetch_job_posting(state["job_url"])

        return {
            **state,
            "job_text": job_text,
            "error": "",
        }

    except Exception as exc:
        return {
            **state,
            "error": f"fetch_job failed: {exc}",
            "error_count": state.get("error_count", 0) + 1,
        }


def extract_job(state: AgentState) -> AgentState:
    """
    Extract structured job information.
    """

    if not state.get("job_text"):
        return {
            **state,
            "error": "Cannot extract job because job_text is unavailable.",
            "error_count": state.get("error_count", 0) + 1,
        }

    try:
        job = extract_job_posting(state["job_text"])

        return {
            **state,
            "job": job,
            "error": "",
        }

    except Exception as exc:
        return {
            **state,
            "error": f"extract_job failed: {exc}",
            "error_count": state.get("error_count", 0) + 1,
        }


def match_resume(state: AgentState) -> AgentState:
    """
    Match the resume against the extracted job.
    """

    if not state.get("job"):
        return {
            **state,
            "error": "Cannot match resume because job data is unavailable.",
            "error_count": state.get("error_count", 0) + 1,
        }

    try:
        match = match_resume_to_job(
            resume_text=state["resume_text"],
            job=state["job"],
        )

        return {
            **state,
            "match": match,
            "error": "",
        }

    except Exception as exc:
        return {
            **state,
            "error": f"match_resume failed: {exc}",
            "error_count": state.get("error_count", 0) + 1,
        }


def calculate_score(state: AgentState) -> AgentState:
    """
    Calculate the final candidate fit score.
    """

    if not state.get("job"):
        return {
            **state,
            "error": "Cannot calculate score because job data is unavailable.",
            "error_count": state.get("error_count", 0) + 1,
        }

    if not state.get("match"):
        return {
            **state,
            "error": "Cannot calculate score because resume match is unavailable.",
            "error_count": state.get("error_count", 0) + 1,
        }

    try:
        score = calculate_fit_score(
            job=state["job"],
            match=state["match"],
        )

        return {
            **state,
            "score": score,
            "error": "",
        }

    except Exception as exc:
        return {
            **state,
            "error": f"calculate_score failed: {exc}",
            "error_count": state.get("error_count", 0) + 1,
        }


def build_graph():
    """
    Build the LangGraph job-screening workflow.
    """

    graph = StateGraph(AgentState)

    graph.add_node("fetch_job", fetch_job)
    graph.add_node("extract_job", extract_job)
    graph.add_node("match_resume", match_resume)
    graph.add_node("calculate_score", calculate_score)

    graph.add_edge(START, "fetch_job")
    graph.add_edge("fetch_job", "extract_job")
    graph.add_edge("extract_job", "match_resume")
    graph.add_edge("match_resume", "calculate_score")
    graph.add_edge("calculate_score", END)

    return graph.compile()


job_screening_graph = build_graph()


def run_graph(job_url: str, resume_text: str) -> AgentState:
    """
    Run the complete job-screening graph.
    """

    initial_state: AgentState = {
        "job_url": job_url,
        "resume_text": resume_text,
        "error_count": 0,
    }

    return job_screening_graph.invoke(initial_state)
