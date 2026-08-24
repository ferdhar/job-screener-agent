from types import SimpleNamespace

from app import matcher
from app.models import (
    JobPosting,
    Requirement,
    RequirementMatch,
    ResumeMatch,
)


def make_job():
    return JobPosting(
        title="AI Research Engineer",
        company="Test Research Institute",
        location="San Francisco, CA",
        responsibilities=[
            "Build AI systems for scientific research."
        ],
        requirements=[
            Requirement(
                id="REQ-001",
                description="Strong Python programming skills.",
                category="technical_skill",
                importance="required",
            ),
            Requirement(
                id="REQ-002",
                description="Experience with Git.",
                category="technical_skill",
                importance="required",
            ),
            Requirement(
                id="REQ-003",
                description="Experience with Docker.",
                category="technical_skill",
                importance="preferred",
            ),
        ],
        technical_skills=[
            "Python",
            "Git",
            "Docker",
        ],
    )


def make_fake_match():
    return ResumeMatch(
        requirement_matches=[
            RequirementMatch(
                requirement_id="REQ-001",
                requirement="Strong Python programming skills.",
                status="matched",
                evidence="Candidate developed Python scripts.",
            ),
            RequirementMatch(
                requirement_id="REQ-002",
                requirement="Experience with Git.",
                status="matched",
                evidence="Candidate used Git for software development.",
            ),
            RequirementMatch(
                requirement_id="REQ-003",
                requirement="Experience with Docker.",
                status="missing",
                evidence="Resume provides no evidence of Docker experience.",
            ),
        ],
        strengths=[
            "Strong Python experience.",
            "Scientific computing experience.",
        ],
        gaps=[
            "No Docker experience.",
        ],
    )


def mock_openai(monkeypatch, fake_match):
    fake_response = SimpleNamespace(
        output_parsed=fake_match
    )

    class FakeResponses:
        def parse(self, **kwargs):
            return fake_response

    class FakeClient:
        responses = FakeResponses()

    monkeypatch.setattr(
        matcher,
        "client",
        FakeClient(),
    )


def test_match_resume_to_job_returns_structured_match(monkeypatch):
    job = make_job()
    fake_match = make_fake_match()

    mock_openai(monkeypatch, fake_match)

    resume = """
    B.A. Physics, UC Berkeley.

    Developed Python scripts for laboratory automation.
    Used Git for software development and version control.
    """

    result = matcher.match_resume_to_job(
        resume,
        job,
    )

    assert isinstance(result, ResumeMatch)

    assert len(result.requirement_matches) == 3

    assert len(result.strengths) == 2
    assert len(result.gaps) == 1


def test_match_resume_to_job_preserves_requirement_ids(monkeypatch):
    job = make_job()
    fake_match = make_fake_match()

    mock_openai(monkeypatch, fake_match)

    result = matcher.match_resume_to_job(
        "Python and Git experience.",
        job,
    )

    ids = [
        item.requirement_id
        for item in result.requirement_matches
    ]

    assert ids == [
        "REQ-001",
        "REQ-002",
        "REQ-003",
    ]


def test_match_resume_to_job_preserves_match_status(monkeypatch):
    job = make_job()
    fake_match = make_fake_match()

    mock_openai(monkeypatch, fake_match)

    result = matcher.match_resume_to_job(
        "Python and Git experience.",
        job,
    )

    statuses = [
        item.status
        for item in result.requirement_matches
    ]

    assert statuses == [
        "matched",
        "matched",
        "missing",
    ]


def test_match_resume_to_job_preserves_evidence(monkeypatch):
    job = make_job()
    fake_match = make_fake_match()

    mock_openai(monkeypatch, fake_match)

    result = matcher.match_resume_to_job(
        "Python and Git experience.",
        job,
    )

    assert (
        result.requirement_matches[0].evidence
        == "Candidate developed Python scripts."
    )

    assert (
        result.requirement_matches[2].evidence
        == "Resume provides no evidence of Docker experience."
    )