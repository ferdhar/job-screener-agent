from app.application_agent_graph import run_application_agent
from app.models import JobPosting, Requirement, ResumeMatch, RequirementMatch


RESUME = """
Ferdinand Hartanto

Experience:

Post-Baccalaureate Fellow, Lawrence Berkeley National Laboratory

- Developed Python and Bash scripts for laboratory automation.
"""


def make_job():
    return JobPosting(
        title="Test Job",
        company="Test Company",
        location="Test Location",
        responsibilities=[],
        requirements=[
            Requirement(
                id="REQ-001",
                description="Python",
                category="technical_skill",
                importance="required",
            ),
        ],
        technical_skills=["Python"],
    )


def make_match():
    return ResumeMatch(
        requirement_matches=[
            RequirementMatch(
                requirement_id="REQ-001",
                requirement="Python",
                status="matched",
                evidence="Developed Python scripts",
            ),
        ],
        strengths=["Developed Python scripts"],
        gaps=[],
    )


def make_state(overall_score):
    return {
        "job": make_job(),
        "resume_text": RESUME,
        "match": make_match(),
        "score": {
            "overall_score": overall_score,
            "required_score": overall_score,
            "preferred_score": overall_score,
        },
    }


def test_application_agent_generates_application_for_high_score():
    state = make_state(overall_score=80)

    result = run_application_agent(state)

    assert result["analysis"]["generate_application"] is True
    assert result["candidate_evidence"]


def test_application_agent_skips_application_for_low_score():
    state = make_state(overall_score=10)

    result = run_application_agent(state)

    assert result["analysis"]["generate_application"] is False
    assert result.get("candidate_evidence") is None
