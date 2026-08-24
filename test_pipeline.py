from app.pipeline import screen_job


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


result = screen_job(
    URL,
    RESUME,
    generate_letter=False,
)


print("\n")
print("JOB SCREENING RESULT")
print("====================")

print(f"Title: {result['job'].title}")
print(f"Company: {result['job'].company}")

print(
    f"Overall Fit: "
    f"{result['score']['overall_score']}/100"
)

print(
    f"Required Score: "
    f"{result['score']['required_score']}/100"
)

print(
    f"Preferred Score: "
    f"{result['score']['preferred_score']}/100"
)
