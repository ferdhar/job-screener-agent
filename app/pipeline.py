from app.scraper import fetch_job_posting
from app.extractor import extract_job_posting
from app.matcher import match_resume_to_job
from app.scorer import calculate_fit_score
from app.cover_letter import generate_cover_letter


def screen_job(
    url: str,
    resume: str,
    generate_letter: bool = True,
) -> dict:
    """
    Run the complete job screening pipeline for one job.
    """

    print(f"Fetching: {url}")

    job_text = fetch_job_posting(url)

    print("Extracting job information...")

    job = extract_job_posting(job_text)

    print("Matching resume...")

    match = match_resume_to_job(
        resume,
        job,
    )

    print("Calculating score...")

    score = calculate_fit_score(
        job,
        match,
    )

    cover_letter = None

    if generate_letter:
        print("Generating cover letter...")

        cover_letter = generate_cover_letter(
            resume,
            job,
            match,
        )

    return {
        "url": url,
        "job": job,
        "match": match,
        "score": score,
        "cover_letter": cover_letter,
    }
