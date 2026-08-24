from dotenv import load_dotenv
from openai import OpenAI

from app.models import JobPosting

load_dotenv()
client = None

def get_client():
    global client

    if client is None:
        client = OpenAI()

    return client

def extract_job_posting(job_text: str) -> JobPosting:
    """
    Convert raw job-posting text into structured job information.
    """
    
    client = get_client()

    response = client.responses.parse(
        model="gpt-5.6-luna",
        instructions="""
        You are extracting structured requirements from a job posting.

        Extract:

        1. Job title
        2. Company
        3. Location
        4. Responsibilities
        5. Individual requirements
        6. Technical skills

        For every requirement:

        - Write a concise description of ONE requirement.

        - Give every requirement a unique sequential ID:
          REQ-001
          REQ-002
          REQ-003
          ...

        - Assign one category:
          education
          experience
          technical_skill
          domain_knowledge
          responsibility
          communication
          other

        - Assign importance:
          required
          preferred

        Important extraction rules:

        1. Preserve the meaning of the original job posting.

        2. Do not invent qualifications.

        3. Each requirement must represent ONE independently
          assessable qualification.

        4. NEVER combine multiple technologies or skills into one
          requirement.

          For example, if the posting says:

          "Experience with AWS, Docker, Git, and modern software
          engineering practices"

          create separate requirements:

          - Experience with AWS
          - Experience with Docker
          - Experience with Git
          - Experience with modern software engineering practices

        5. Similarly, if the posting says:

          "Knowledge of MCP servers, tool calling, embeddings,
          vector databases, and context engineering"

          create separate requirements for each concept.

        6. Separate required qualifications from preferred qualifications.

        7. Do not turn every noun in a job posting into a requirement.
          Only extract things that represent qualifications, experience,
          knowledge, education, skills, or explicitly expected capabilities.

        8. Responsibilities should remain separate from qualifications.

        9. Technical skills should be extracted separately, but do not
          treat a technical skill as a required qualification unless
          the job posting explicitly makes it a requirement.

          IMPORTANT REQUIREMENT GROUPING RULES:

            Extract qualifications at the level of meaningful candidate
            requirements, not individual technologies or examples.

            Do NOT split one requirement into multiple requirements merely
            because it contains several examples.

            For example:

            "Strong knowledge of AI-assisted coding tools such as
            Claude Code, Codex, or OpenCode"

            must remain ONE requirement.

            Similarly:

            "Strong knowledge of agentic AI fundamentals such as MCP
            servers, tool-calling loops, embeddings, vector databases,
            skills and context engineering"

            must remain ONE requirement.

            Similarly:

            "Experience developing AI agents that interact with APIs,
            databases, or external tools"

            must remain ONE requirement.

            Similarly:

            "Demonstrated initiative through research projects,
            internships, open-source contributions, or personal projects
            involving LLMs or agentic AI systems"

            must remain ONE requirement.

            Treat tools, technologies, and examples listed within a
            requirement as supporting concepts rather than separate
            requirements.

            Only create a separate requirement when the job posting
            expresses a genuinely distinct qualification.
        
          Aim for approximately 10–20 meaningful requirements for a
          typical technical job posting.

          Do not create dozens of requirements simply by splitting
          sentences into individual technologies.
        """,
        input=job_text,
        text_format=JobPosting,
    )

    job = response.output_parsed

    for index, requirement in enumerate(job.requirements, start=1):
        requirement.id = f"REQ-{index:03d}"

    return job
