from app.models import JobPosting


def retrieve_candidate_evidence(
    resume_text: str,
    job: JobPosting,
) -> list[str]:
    """
    Retrieve candidate evidence from the resume that is relevant
    to the job requirements.

    This does not invent experience. It only returns evidence
    explicitly present in the resume.
    """

    # Initial implementation:
    # return the resume text as the available evidence.
    #
    # We will replace this with structured retrieval later.

    return [
        resume_text
    ]