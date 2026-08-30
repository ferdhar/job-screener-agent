from typing import Literal

from langgraph.graph import StateGraph, START, END

from app.application_agent_state import ApplicationAgentState
from app.application_agent_tools import retrieve_candidate_evidence


def analyze_node(state: ApplicationAgentState):
    """
    Analyze the deterministic screening results and determine
    whether the application is worth generating.
    """

    if state["score"] is None:
        return {
            "error": "Cannot analyze application without a fit score."
        }

    overall_score = state["score"].get("overall_score", 0)

    if overall_score < 50:
        return {
            "analysis": {
                "generate_application": False,
                "reason": "Fit score is below the application threshold.",
            }
        }

    return {
        "analysis": {
            "generate_application": True,
            "reason": "Candidate has sufficient overall fit.",
        }
    }


def should_generate_application(
    state: ApplicationAgentState,
) -> Literal["retrieve_evidence", END]:

    analysis = state.get("analysis")

    if not analysis:
        return END

    if not analysis.get("generate_application", False):
        return END

    return "retrieve_evidence"


def retrieve_evidence_node(state: ApplicationAgentState):
    """
    Use the candidate-evidence retrieval tool.
    """

    if state.get("job") is None:
        return {
            "error": "Cannot retrieve candidate evidence without job data."
        }

    evidence = retrieve_candidate_evidence(
        resume_text=state["resume_text"],
        job=state["job"],
    )

    return {
        "candidate_evidence": evidence
    }


def draft_node(state: ApplicationAgentState):
    """
    Placeholder for cover-letter generation.

    We are deliberately keeping generation separate from
    evidence retrieval.
    """

    return {
        "draft": None,
        "error": (
            "Cover-letter generation has not been implemented yet."
        ),
    }


def build_application_agent_graph():

    graph = StateGraph(ApplicationAgentState)

    graph.add_node("analyze", analyze_node)
    graph.add_node(
        "retrieve_evidence",
        retrieve_evidence_node,
    )
    graph.add_node("draft", draft_node)

    graph.add_edge(START, "analyze")

    graph.add_conditional_edges(
        "analyze",
        should_generate_application,
        {
            "retrieve_evidence": "retrieve_evidence",
            END: END,
        },
    )

    graph.add_edge(
        "retrieve_evidence",
        "draft",
    )

    graph.add_edge(
        "draft",
        END,
    )

    return graph.compile()


application_agent_graph = build_application_agent_graph()


def run_application_agent(state: ApplicationAgentState):
    """
    Run the application-agent workflow.
    """

    return application_agent_graph.invoke(state)