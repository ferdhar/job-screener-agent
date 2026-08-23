from app.models import JobPosting, ResumeMatch


def calculate_fit_score(
    job: JobPosting,
    match: ResumeMatch,
) -> dict:
    """
    Calculate a deterministic resume-to-job fit score.

    Required requirements have a higher weight than preferred
    requirements.
    """

    required_matches = []
    preferred_matches = []

    for requirement, result in zip(
        job.requirements,
        match.requirement_matches,
    ):
        if requirement.importance == "required":
            required_matches.append(result)
        else:
            preferred_matches.append(result)

    def score_matches(matches):
        if not matches:
            return 100.0

        points = 0

        for match in matches:
            if match.status == "matched":
                points += 1
            elif match.status == "partial":
                points += 0.5

        return (points / len(matches)) * 100

    required_score = score_matches(required_matches)
    preferred_score = score_matches(preferred_matches)

    # Required qualifications are weighted more heavily.
    overall_score = (
        required_score * 0.75
        + preferred_score * 0.25
    )

    return {
        "overall_score": round(overall_score, 1),
        "required_score": round(required_score, 1),
        "preferred_score": round(preferred_score, 1),
        "required_count": len(required_matches),
        "preferred_count": len(preferred_matches),
    }
