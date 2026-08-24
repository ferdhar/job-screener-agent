from dotenv import load_dotenv
from openai import OpenAI

from app.tools import TOOL_FUNCTIONS


load_dotenv()

client = OpenAI()

TOOLS = [
    {
        "type": "function",
        "name": "fetch_job",
        "description": "Fetch the raw text of a job posting from a URL.",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The URL of the job posting.",
                }
            },
            "required": ["url"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "extract_job",
        "description": "Extract structured job information and individual requirements from raw job posting text.",
        "parameters": {
            "type": "object",
            "properties": {
                "job_text": {
                    "type": "string",
                    "description": "Raw job posting text.",
                }
            },
            "required": ["job_text"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "match_resume",
        "description": "Compare a candidate resume against the structured job requirements.",
        "parameters": {
            "type": "object",
            "properties": {
                "resume_text": {
                    "type": "string",
                    "description": "Candidate resume text.",
                },
                "job_data": {
                    "type": "object",
                    "description": "Structured job posting.",
                    "properties": {
                        "title": {"type": "string"},
                        "company": {"type": "string"},
                        "location": {"type": "string"},
                        "responsibilities": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "requirements": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "string"},
                                    "description": {"type": "string"},
                                    "category": {"type": "string"},
                                    "importance": {"type": "string"},
                                },
                                "required": [
                                    "id",
                                    "description",
                                    "category",
                                    "importance",
                                ],
                                "additionalProperties": False,
                            },
                        },
                        "technical_skills": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                    },
                    "required": [
                        "title",
                        "company",
                        "location",
                        "responsibilities",
                        "requirements",
                        "technical_skills",
                    ],
                    "additionalProperties": False,
                },
            },
            "required": ["resume_text", "job_data"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "calculate_score",
        "description": "Calculate the candidate's fit score from the requirement matches.",
        "parameters": {
            "type": "object",
            "properties": {
                "match_data": {
                    "type": "object",
                    "description": "Structured resume match results.",
                    "properties": {
                        "requirement_matches": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "requirement_id": {"type": "string"},
                                    "requirement": {"type": "string"},
                                    "status": {"type": "string"},
                                    "evidence": {"type": "string"},
                                },
                                "required": [
                                    "requirement_id",
                                    "requirement",
                                    "status",
                                    "evidence",
                                ],
                                "additionalProperties": False,
                            },
                        },
                        "strengths": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "gaps": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                    },
                    "required": [
                        "requirement_matches",
                        "strengths",
                        "gaps",
                    ],
                    "additionalProperties": False,
                },
                "job_data": {
                    "type": "object",
                    "description": "Structured job posting.",
                    "properties": {
                        "title": {"type": "string"},
                        "company": {"type": "string"},
                        "location": {"type": "string"},
                        "responsibilities": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "requirements": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "string"},
                                    "description": {"type": "string"},
                                    "category": {"type": "string"},
                                    "importance": {"type": "string"},
                                },
                                "required": [
                                    "id",
                                    "description",
                                    "category",
                                    "importance",
                                ],
                                "additionalProperties": False,
                            },
                        },
                        "technical_skills": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                    },
                    "required": [
                        "title",
                        "company",
                        "location",
                        "responsibilities",
                        "requirements",
                        "technical_skills",
                    ],
                    "additionalProperties": False,
                },
            },
            "required": ["match_data", "job_data"],
            "additionalProperties": False,
        },
        "strict": True,
    },
]


def run_agent(job_url: str, resume_text: str):
    """
    Run the job application screening agent.
    """

    input_items = [
        {
            "role": "user",
            "content": [
                {
                    "type": "input_text",
                    "text": f"""
Screen this job application.

JOB URL:
{job_url}

CANDIDATE RESUME:
{resume_text}

Use the available tools to:
1. Fetch the job posting.
2. Extract its structured requirements.
3. Match the resume against every requirement.
4. Calculate the candidate's fit score.

Do not invent information.

Use tools whenever the required information is available through them.
""",
                }
            ],
        }
    ]

    while True:

        response = client.responses.create(
            model="gpt-5.6-luna",
            instructions="""
You are a job application screening agent.

You have access to tools that fetch job postings, extract requirements,
match resumes, and calculate scores.

Reason about which tool should be called next.

Do not fabricate job requirements or candidate experience.

Complete the screening workflow before giving the final answer.
""",
            tools=TOOLS,
            input=input_items,
        )

        input_items += response.output

        tool_calls = [
            item
            for item in response.output
            if item.type == "function_call"
        ]

        if not tool_calls:
            return response.output_text

        for tool_call in tool_calls:

            name = tool_call.name
            arguments = json.loads(tool_call.arguments)

            print(f"\n[AGENT] Calling tool: {name}")

            function = TOOL_FUNCTIONS[name]

            result = function(**arguments)

            input_items.append(
                {
                    "type": "function_call_output",
                    "call_id": tool_call.call_id,
                    "output": json.dumps(result),
                }
            )
