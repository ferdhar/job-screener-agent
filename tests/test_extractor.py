from types import SimpleNamespace

from app import extractor
from app.models import JobPosting, Requirement


def make_fake_job():
    return JobPosting(
        title="AI Research Engineer",
        company="Test Research Institute",
        location="San Francisco, CA",
        responsibilities=[
            "Build AI systems for scientific research.",
            "Collaborate with researchers.",
        ],
        requirements=[
            Requirement(
                id="temporary-id",
                description="Strong Python programming skills.",
                category="technical_skill",
                importance="required",
            ),
            Requirement(
                id="temporary-id",
                description="Experience with Git.",
                category="technical_skill",
                importance="required",
            ),
            Requirement(
                id="temporary-id",
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


def test_extract_job_posting_assigns_requirement_ids(monkeypatch):
    fake_job = make_fake_job()

    fake_response = SimpleNamespace(
        output_parsed=fake_job
    )

    class FakeResponses:
        def parse(self, **kwargs):
            return fake_response

    class FakeClient:
        responses = FakeResponses()

    monkeypatch.setattr(
        extractor,
        "client",
        FakeClient(),
    )

    result = extractor.extract_job_posting(
        "Fake job posting text"
    )

    assert result.title == "AI Research Engineer"
    assert result.company == "Test Research Institute"

    assert result.requirements[0].id == "REQ-001"
    assert result.requirements[1].id == "REQ-002"
    assert result.requirements[2].id == "REQ-003"


def test_extract_job_posting_preserves_structured_data(monkeypatch):
    fake_job = make_fake_job()

    fake_response = SimpleNamespace(
        output_parsed=fake_job
    )

    class FakeResponses:
        def parse(self, **kwargs):
            return fake_response

    class FakeClient:
        responses = FakeResponses()

    monkeypatch.setattr(
        extractor,
        "client",
        FakeClient(),
    )

    result = extractor.extract_job_posting(
        "Fake job posting text"
    )

    assert result.title == "AI Research Engineer"
    assert result.company == "Test Research Institute"
    assert result.location == "San Francisco, CA"

    assert len(result.responsibilities) == 2
    assert len(result.requirements) == 3
    assert len(result.technical_skills) == 3


def test_extract_job_posting_assigns_sequential_ids(monkeypatch):
    fake_job = make_fake_job()

    fake_response = SimpleNamespace(
        output_parsed=fake_job
    )

    class FakeResponses:
        def parse(self, **kwargs):
            return fake_response

    class FakeClient:
        responses = FakeResponses()

    monkeypatch.setattr(
        extractor,
        "client",
        FakeClient(),
    )

    result = extractor.extract_job_posting(
        "Fake job posting text"
    )

    ids = [
        requirement.id
        for requirement in result.requirements
    ]

    assert ids == [
        "REQ-001",
        "REQ-002",
        "REQ-003",
    ]