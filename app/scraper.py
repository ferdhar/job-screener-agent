import requests
from bs4 import BeautifulSoup


def fetch_job_posting(url: str) -> str:
    """
    Fetch a job posting webpage and extract useful text.
    """

    response = requests.get(
        url,
        headers={
            "User-Agent": "Mozilla/5.0"
        },
        timeout=20,
    )

    response.raise_for_status()

    response.encoding = response.apparent_encoding

    soup = BeautifulSoup(response.text, "html.parser")

    # Try to get the page title
    title = ""

    title_tag = soup.find("meta", property="og:title")

    if title_tag:
        title = title_tag.get("content", "")

    # Try to get the job description from OpenGraph metadata
    description = ""

    description_tag = soup.find(
        "meta",
        property="og:description"
    )

    if description_tag:
        description = description_tag.get("content", "")

    # Also try normal page text
    for element in soup(["script", "style", "nav", "footer"]):
        element.decompose()

    page_text = soup.get_text(separator="\n")

    lines = []

    for line in page_text.splitlines():
        line = line.strip()

        if line:
            lines.append(line)

    page_text = "\n".join(lines)

    # Combine the useful information
    parts = []

    if title:
        parts.append(f"Job Title: {title}")

    if description:
        parts.append(f"Job Description:\n{description}")

    if page_text:
        parts.append(f"Page Text:\n{page_text}")

    return "\n\n".join(parts)
