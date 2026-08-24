import json

from dotenv import load_dotenv
from openai import OpenAI

from app.tools import TOOL_FUNCTIONS
from app.state import AgentState

load_dotenv()

client = OpenAI()

TOOLS = [
    {
        "type": "function",
        "name": "fetch_job",
        "description": (
            "Fetch the job posting specified by the user's job URL. "
            "The fetched content is stored in agent state."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "extract_job",
        "description": (
            "Extract structured job information and individual "
            "requirements from the fetched job posting."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "match_resume",
        "description": (
            "Compare the candidate resume against the structured "
            "job requirements stored in agent state."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "calculate_score",
        "description": (
            "Calculate the candidate's fit score using the job "
            "requirements and resume match stored in agent state."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        },
        "strict": True,
    },
]

def run_agent(job_url: str, resume_text: str):
    """
    Run the stateful job application screening agent.
    """

    state = AgentState(
        job_url=job_url,
        resume_text=resume_text,
    )

    input_items = [
        {
            "role": "user",
            "content": [
                {
                    "type": "input_text",
                    "text": """
Screen this job application.

Use the available tools to:

1. Fetch the job posting.
2. Extract its structured requirements.
3. Match the resume against every requirement.
4. Calculate the candidate's fit score.

The job URL and candidate resume are already available in agent state.

Do not invent information.

Use tools whenever the required information is available through them.

Complete the entire screening workflow before giving the final answer.
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

You have access to tools that operate on shared agent state.

The state contains:

- the job URL
- the candidate resume
- fetched job text
- structured job information
- requirement-level resume matches
- fit scores

Reason about which tool should be called next.

Do not fabricate job requirements or candidate experience.

Follow the workflow:

fetch_job
→ extract_job
→ match_resume
→ calculate_score

Do not skip required steps.

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

            return {
                "job": state.job.model_dump() if state.job else None,
                "match": state.match.model_dump() if state.match else None,
                "score": state.score,
                "final_response": response.output_text,
            }

        for tool_call in tool_calls:

            name = tool_call.name

            print(f"\n[AGENT] Calling tool: {name}")

            function = TOOL_FUNCTIONS[name]

            result = function(state)

            input_items.append(
                {
                    "type": "function_call_output",
                    "call_id": tool_call.call_id,
                    "output": json.dumps(result),
                }
            )