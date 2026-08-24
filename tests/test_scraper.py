import pytest
import requests

from app.scraper import fetch_job_posting


TEST_URL = "https://example.com/job"


class MockResponse:
    def __init__(self, text, status_code=200):
        self.text = text
        self.status_code = status_code
        self.encoding = None
        self.apparent_encoding = "utf-8"

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(
                f"{self.status_code} Client Error"
            )


def test_fetch_job_posting_extracts_job_information(monkeypatch):
    html = """
    <html>
        <head>
            <meta
                property="og:title"
                content="AI Research Engineer"
            >
            <meta
                property="og:description"
                content="Build AI systems for scientific research."
            >
        </head>

        <body>
            <nav>This should be removed</nav>

            <h1>AI Research Engineer</h1>

            <p>Build agentic AI systems.</p>

            <p>Python experience required.</p>

            <script>
                This should be removed
            </script>

            <style>
                This should also be removed
            </style>

            <footer>
                This should be removed
            </footer>
        </body>
    </html>
    """

    def mock_get(url, headers, timeout):
        assert url == TEST_URL
        assert headers["User-Agent"] == "Mozilla/5.0"
        assert timeout == 20

        return MockResponse(html)

    monkeypatch.setattr(
        requests,
        "get",
        mock_get,
    )

    result = fetch_job_posting(TEST_URL)

    assert "Job Title: AI Research Engineer" in result

    assert (
        "Build AI systems for scientific research."
        in result
    )

    assert "Build agentic AI systems." in result

    assert "Python experience required." in result

    assert "This should be removed" not in result

    assert "This should also be removed" not in result


def test_fetch_job_posting_handles_missing_metadata(monkeypatch):
    html = """
    <html>
        <body>
            <h1>Research Engineer</h1>
            <p>Python experience required.</p>
        </body>
    </html>
    """

    def mock_get(url, headers, timeout):
        return MockResponse(html)

    monkeypatch.setattr(
        requests,
        "get",
        mock_get,
    )

    result = fetch_job_posting(TEST_URL)

    assert "Research Engineer" in result
    assert "Python experience required." in result


def test_fetch_job_posting_raises_for_http_error(monkeypatch):
    def mock_get(url, headers, timeout):
        return MockResponse(
            "",
            status_code=404,
        )

    monkeypatch.setattr(
        requests,
        "get",
        mock_get,
    )

    with pytest.raises(requests.HTTPError):
        fetch_job_posting(TEST_URL)