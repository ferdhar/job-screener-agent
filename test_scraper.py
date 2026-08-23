from app.scraper import fetch_job_posting


url = "https://gladstone.wd503.myworkdayjobs.com/en-US/careers/details/Research-Engineer--ai--I-II-or-III---Jain-Lab_REQ-3845"

text = fetch_job_posting(url)

print(text[:3000])
