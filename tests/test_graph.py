from app.graph import build_graph
from app.graph import run_graph


def test_graph_builds():
    graph = build_graph()

    assert graph is not None


URL = (
    "https://gladstone.wd503.myworkdayjobs.com/"
    "en-US/careers/details/"
    "Research-Engineer--ai--I-II-or-III---Jain-Lab_REQ-3845"
)


RESUME = """
Ferdinand Hartanto

Education:
B.A. Physics, UC Berkeley

Experience:

Post-Baccalaureate Fellow, Lawrence Berkeley National Laboratory

- Worked with Linux-based scientific computing environments.
- Troubleshot hardware and software problems.
- Developed Python and Bash scripts for laboratory automation.
- Improved automated testing workflows.
- Developed scripts for testing multiple detector modules.
- Worked with configuration files, monitoring systems, and databases.
- Used Git for software development and version control.

Technical Skills:

Python, Bash, C++, SQL, MATLAB, Git, Linux,
scientific computing, automation, software testing,
hardware and instrumentation.
"""


def test_graph_runs():

    result = run_graph(URL, RESUME)

    assert result["job_text"]
    assert result["job"] is not None
    assert result["match"] is not None
    assert result["score"] is not None

    assert "overall_score" in result["score"]
    assert "required_score" in result["score"]
    assert "preferred_score" in result["score"]