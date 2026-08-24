from app.agent import run_agent


RESUME = """
Ferdinand Hartanto

B.A. Physics, UC Berkeley

Post-Baccalaureate Fellow
Lawrence Berkeley National Laboratory

- Developed Python scripts for laboratory automation.
- Developed automated testing workflows.
- Worked with Linux scientific computing environments.
- Used Git for software development and version control.
- Worked with databases and monitoring systems.
"""


def test_agent_runs():
    url = (
        "https://gladstone.wd503.myworkdayjobs.com/"
        "en-US/careers/details/"
        "Research-Engineer--ai--I-II-or-III---Jain-Lab_REQ-3845"
    )

    result = run_agent(url, RESUME)

    assert result
