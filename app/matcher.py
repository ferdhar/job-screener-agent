from dotenv import load_dotenv
from openai import OpenAI

from app.models import JobPosting, ResumeMatch


load_dotenv()

client = OpenAI()


def match_resume_to_job(
    resume_text: str,
    job: JobPosting,
) -> ResumeMatch:
    """
    Compare a resume against individual job requirements.
    """

    requirements = "\n".join(
                            f"- [{r.id}] "
                            f"[{r.importance.upper()}] "
                            f"[{r.category}] "
                            f"{r.description}"
                            for r in job.requirements
                            )

    response = client.responses.parse(
        model="gpt-5.6-luna",
        instructions="""
        You are a careful resume screening system.

        Compare the candidate's resume against every job requirement.

        For every requirement, return the exact requirement ID provided
        in the job requirements.

        Do not create new IDs.

        Do not omit requirements.

        Every requirement must have exactly one corresponding match.

        For each requirement, classify it as:

        matched:
        The resume contains clear evidence that the candidate satisfies
        the requirement.

        partial:
        The resume contains related or transferable experience, but does
        not clearly satisfy the full requirement.

        missing:
        The resume contains no meaningful evidence for the requirement.

        Important:

        - Evaluate every requirement individually.
        - Do not invent experience.
        - Do not infer skills merely from the candidate's education.
        - Do not assume that general programming experience means AI,
          cloud, Docker, or biological experience.
        - Evidence must come directly from the resume.
        - For a matched or partial requirement, explain what evidence
          supports the classification.
        - For missing requirements, explain briefly that the resume
          does not provide evidence.

        Also identify the candidate's strongest relevant strengths and
        most important gaps.
        """,
        input=f"""
JOB REQUIREMENTS
================

{requirements}


CANDIDATE RESUME
================

{resume_text}
""",
        text_format=ResumeMatch,
    )

    return response.output_parsed
