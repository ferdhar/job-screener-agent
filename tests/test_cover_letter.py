from app.scraper import fetch_job_posting
from app.extractor import extract_job_posting
from app.matcher import match_resume_to_job
from app.cover_letter import generate_cover_letter


url = "https://gladstone.wd503.myworkdayjobs.com/en-US/careers/details/Research-Engineer--ai--I-II-or-III---Jain-Lab_REQ-3845"


resume = """
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


print("Fetching job posting...")
job_text = fetch_job_posting(url)

print("Extracting job information...")
job = extract_job_posting(job_text)

print("Matching resume...")
match = match_resume_to_job(resume, job)

print("Generating cover letter...")
cover_letter = generate_cover_letter(
    resume,
    job,
    match,
)


print("\nTAILORED COVER LETTER")
print("=====================\n")

print(cover_letter)
