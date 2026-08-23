from dotenv import load_dotenv
from openai import OpenAI

from app.models import JobPosting, ResumeMatch


load_dotenv()

client = OpenAI()


def generate_cover_letter(
    resume_text: str,
    job: JobPosting,
    match: ResumeMatch,
) -> str:
    """
    Generate a tailored cover letter based on the job posting
    and evidence-supported resume matches.
    """

    matched_evidence = "\n".join(
        f"- {item.requirement}: {item.evidence}"
        for item in match.requirement_matches
        if item.status in ("matched", "partial")
    )

    response = client.responses.create(
        model="gpt-5.6-luna",
        instructions="""
        You are an expert technical recruiter and cover-letter writer.

        Write a concise, highly tailored cover letter for the candidate.

        Use the job posting and resume evidence provided.

        Rules:

        1. Only claim experience that is supported by the resume.

        2. Never invent experience with technologies, tools, scientific
        domains, or programming languages.

        3. Do not claim the candidate has experience with AI agents,
        MCP, LangGraph, biological datasets, cloud infrastructure,
        Docker, or other technologies unless the resume explicitly
        supports that claim.

        4. Emphasize transferable experience when appropriate.

        5. Connect the candidate's scientific computing and laboratory
        experience to the employer's technical and research goals.

        6. The letter should sound like a real technical applicant,
        not generic AI-generated marketing copy.

        7. Keep it concise: approximately 3-5 paragraphs.

        8. Do not include a fake name, address, phone number, or date.

        9. Do not mention the candidate's weaknesses directly.

        10. Do not simply repeat the resume. Explain why the candidate's
            experience is relevant to this particular position.
        """,
        input=f"""
JOB POSTING
===========

Title: {job.title}
Company: {job.company}
Location: {job.location}

Responsibilities:
{chr(10).join("- " + r for r in job.responsibilities)}


RESUME
======

{resume_text}


RELEVANT RESUME EVIDENCE
========================

{matched_evidence}
""",
    )

    return response.output_text
