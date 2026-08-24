from app.models import JobPosting, Requirement, RequirementMatch, ResumeMatch
from app.scorer import calculate_fit_score

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
            Requirement(
                id="REQ-002",
                description="Git",
                category="technical_skill",
                importance="required",
            ),
            Requirement(
                id="REQ-003",
                description="Docker",
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

def test_scorer_with_matched_requirements():
    job = make_job()

    match = ResumeMatch(
        requirement_matches=[
            RequirementMatch(
                requirement_id="REQ-001",
                requirement="Python",
                status="matched",
                evidence="Strong Python experience",
            ),
            RequirementMatch(
                requirement_id="REQ-002",
                requirement="Git",
                status="matched",
                evidence="Git experience",
            ),
            RequirementMatch(
                requirement_id="REQ-003",
                requirement="Docker",
                status="matched",
                evidence="Docker experience",
            ),
        ],
        strengths=[
        "Strong Python experience",
        "Git experience",
        "Docker experience",
        ],
        gaps=[]
    )

    result = calculate_fit_score(job, match)

    assert result["required_score"] == 100.0
    assert result["preferred_score"] == 100.0
    assert result["overall_score"] == 100.0

def test_scorer_with_all_requirements_missing():
    job = make_job()

    match = ResumeMatch(
        requirement_matches=[
            RequirementMatch(
                requirement_id="REQ-001",
                requirement="Python",
                status="missing",
                evidence="No Python experience found",
            ),
            RequirementMatch(
                requirement_id="REQ-002",
                requirement="Git",
                status="missing",
                evidence="No Git experience found",
            ),
            RequirementMatch(
                requirement_id="REQ-003",
                requirement="Docker",
                status="missing",
                evidence="No Docker experience found",
            ),
        ],
        strengths=[],
        gaps=[
            "Python",
            "Git",
            "Docker",
        ],
    )

    result = calculate_fit_score(job, match)

    assert result["required_score"] == 0.0
    assert result["preferred_score"] == 0.0
    assert result["overall_score"] == 0.0

def test_scorer_with_partial_requirements():
    job = make_job()

    match = ResumeMatch(
        requirement_matches=[
            RequirementMatch(
                requirement_id="REQ-001",
                requirement="Python",
                status="partial",
                evidence="Some Python experience",
            ),
            RequirementMatch(
                requirement_id="REQ-002",
                requirement="Git",
                status="partial",
                evidence="Some Git experience",
            ),
            RequirementMatch(
                requirement_id="REQ-003",
                requirement="Docker",
                status="partial",
                evidence="Some Docker experience",
            ),
        ],
        strengths=[],
        gaps=[],
    )

    result = calculate_fit_score(job, match)

    assert result["required_score"] == 50.0
    assert result["preferred_score"] == 50.0
    assert result["overall_score"] == 50.0

def test_scorer_with_mixed_matches():
    job = make_job()

    match = ResumeMatch(
        requirement_matches=[
            RequirementMatch(
                requirement_id="REQ-001",
                requirement="Python",
                status="matched",
                evidence="Strong Python experience",
            ),
            RequirementMatch(
                requirement_id="REQ-002",
                requirement="Git",
                status="missing",
                evidence="No Git experience found",
            ),
            RequirementMatch(
                requirement_id="REQ-003",
                requirement="Docker",
                status="partial",
                evidence="Some Docker experience",
            ),
        ],
        strengths=[
            "Strong Python experience",
        ],
        gaps=[
            "Git",
        ],
    )

    result = calculate_fit_score(job, match)

    assert result["required_score"] == 50.0
    assert result["preferred_score"] == 50.0
    assert result["overall_score"] == 50.0