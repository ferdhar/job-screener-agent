from app.scraper import fetch_job_posting
from app.extractor import extract_job_posting


url = "https://gladstone.wd503.myworkdayjobs.com/en-US/careers/details/Research-Engineer--ai--I-II-or-III---Jain-Lab_REQ-3845"


print("Fetching job posting...")

job_text = fetch_job_posting(url)


print("Extracting structured job information...")

job = extract_job_posting(job_text)


print("\nJOB INFORMATION")
print("================")

print(f"Title: {job.title}")
print(f"Company: {job.company}")
print(f"Location: {job.location}")


print("\nRESPONSIBILITIES")
print("================")

for responsibility in job.responsibilities:
    print(f"- {responsibility}")


print("\nREQUIREMENTS")
print("============")

for requirement in job.requirements:
    print(
        f"[{requirement.importance.upper()}] "
        f"[{requirement.category}] "
        f"{requirement.description}"
    )


print("\nTECHNICAL SKILLS")
print("================")

for skill in job.technical_skills:
    print(f"- {skill}")
