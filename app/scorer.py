from app.models import JobPosting, ResumeMatch


def calculate_fit_score(
    job: JobPosting,
    match: ResumeMatch,
) -> dict:
    """
    Calculate a deterministic resume-to-job fit score.

    Requirement matching is connected using requirement IDs rather
    than relying on list ordering.
    """

    match_by_id = {
        item.requirement_id: item
        for item in match.requirement_matches
    }

    required_matches = []
    preferred_matches = []

    for requirement in job.requirements:

        result = match_by_id.get(requirement.id)

        if result is None:
            continue

        if requirement.importance == "required":
            required_matches.append(result)
        else:
            preferred_matches.append(result)

    def score_matches(matches):

        if not matches:
            return 100.0

        points = 0

        for result in matches:

            if result.status == "matched":
                points += 1

            elif result.status == "partial":
                points += 0.5

        return (points / len(matches)) * 100

    required_score = score_matches(required_matches)
    preferred_score = score_matches(preferred_matches)

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