# AI Job Screener

An AI-powered job screening application that analyzes job postings against a candidate's resume and produces a structured fit assessment.

The project combines web scraping, structured LLM extraction, resume-to-job matching, deterministic scoring, and a Streamlit web interface.

> **Current status:** The core screening pipeline is functional, the Streamlit UI supports PDF/DOCX/TXT resumes, and the automated test suite for the implemented components is passing. Application-generation and evidence-retrieval features are still under development.

---

## Features

### Job Screening

Given a job posting URL and a resume, the application:

1. Fetches the job posting.
2. Extracts structured job information and requirements.
3. Compares the requirements against the candidate's resume.
4. Calculates a deterministic fit score.
5. Presents the results through a web-based dashboard.

### Resume Upload

The Streamlit interface accepts:

* PDF
* DOCX
* TXT

Resume files are converted to plain text before being passed to the screening pipeline.

Uploaded resume content is processed in the Streamlit session and is not intentionally persisted to disk by the UI.

### Results Dashboard

The UI displays:

* Job title
* Company information when available
* Overall fit score
* Required-requirement score
* Preferred-requirement score
* Requirement-by-requirement matches
* Matched / partial / missing classifications
* Resume evidence
* Candidate strengths
* Candidate gaps
* Screening errors and warnings

The interface is designed as a webpage-style dashboard rather than exposing raw Python objects or JSON.

---

# Architecture

The project separates the user interface from the screening backend.

```text
                         ┌─────────────────────┐
                         │    Streamlit UI     │
                         │     ui/app.py       │
                         └──────────┬──────────┘
                                    │
                       Resume + Job URL
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │    pipeline.py      │
                         │     screen_job()    │
                         └──────────┬──────────┘
                                    │
                    ┌───────────────┼────────────────┐
                    │               │                │
                    ▼               ▼                ▼
                Scraper         Extractor         Matcher
                    │               │                │
                    │               ▼                │
                    │        Structured Job          │
                    │        Requirements             │
                    │                               │
                    └───────────────┬───────────────┘
                                    │
                                    ▼
                              Deterministic
                                  Scorer
                                    │
                                    ▼
                              Fit Assessment
                                    │
                                    ▼
                              Streamlit UI
```

---

# Project Structure

```text
job-screener/
│
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── state.py
│   ├── scraper.py
│   ├── extractor.py
│   ├── matcher.py
│   ├── scorer.py
│   ├── cover_letter.py
│   ├── pipeline.py
│   ├── graph.py
│   ├── agent.py
│   ├── tools.py
│   ├── application_agent_state.py
│   ├── application_agent_tools.py
│   └── application_agent_graph.py
│
├── ui/
│   ├── __init__.py
│   ├── app.py
│   └── resume_parser.py
│
├── tests/
│   ├── test_scorer.py
│   ├── test_scraper.py
│   ├── test_extractor.py
│   ├── test_matcher.py
│   ├── test_cover_letter.py
│   ├── test_pipeline.py
│   ├── test_graph.py
│   ├── test_agent.py
│   ├── test_tools.py
│   ├── test_resume_parser.py
│   └── test_application_agent_graph.py
│
├── data/
├── main.py
├── requirements.txt
├── pytest.ini
├── .gitignore
└── .env
```

---

# Core Components

## `app/models.py`

Defines the shared data structures used throughout the application.

Important models include:

* `Requirement`
* `JobPosting`
* `RequirementMatch`
* `ResumeMatch`

These models provide structured interfaces between the LLM components and deterministic application logic.

---

## `app/scraper.py`

Responsible for retrieving job postings from URLs.

The scraper uses HTTP requests and BeautifulSoup to extract relevant text from job-posting pages.

```text
Job URL
   ↓
HTTP request
   ↓
HTML
   ↓
BeautifulSoup
   ↓
Job text
```

---

## `app/extractor.py`

Uses an OpenAI structured-output call to convert unstructured job-posting text into a structured `JobPosting`.

The extraction process identifies requirements and categorizes them by factors such as:

* Requirement ID
* Category
* Importance
* Description

Requirement IDs are normalized into sequential identifiers such as:

```text
REQ-001
REQ-002
REQ-003
...
```

This provides stable identifiers for subsequent matching and scoring.

---

## `app/matcher.py`

Compares the candidate's resume against the extracted job requirements.

Each requirement is classified as:

* Matched
* Partial
* Missing

The matcher also records supporting evidence from the resume where available.

---

## `app/scorer.py`

Calculates the fit score using deterministic Python logic rather than an LLM.

This separation is intentional.

The LLM is responsible for interpreting the job posting and resume, while the final numerical score is calculated by deterministic code.

This makes the scoring process more reproducible and easier to test.

---

## `app/cover_letter.py`

Contains functionality for generating a tailored cover letter from:

* Resume
* Job posting
* Requirement matches

The underlying function is implemented, although the newer application-agent workflow does not currently invoke it automatically.

---

## `app/pipeline.py`

Provides the simplest end-to-end screening interface:

```python
screen_job(
    url,
    resume,
    generate_letter=True,
)
```

The pipeline performs:

```text
fetch_job_posting()
        ↓
extract_job_posting()
        ↓
match_resume_to_job()
        ↓
calculate_fit_score()
        ↓
generate_cover_letter()  [optional]
```

The Streamlit UI currently calls this pipeline with:

```python
generate_letter=False
```

so the initial screening does not automatically generate a cover letter.

---

# Streamlit UI

The web interface is located in:

```text
ui/app.py
```

Launch it with:

```bash
source .venv/bin/activate
streamlit run ui/app.py
```

Then open:

```text
http://localhost:8501
```

## UI Workflow

The application currently follows this workflow:

```text
             ┌───────────────┐
             │   Job URL     │
             └───────┬───────┘
                     │
                     │
             ┌───────▼───────┐
             │ Resume Upload │
             │ PDF/DOCX/TXT  │
             └───────┬───────┘
                     │
                     ▼
              ┌─────────────┐
              │ Screen Job  │
              └──────┬──────┘
                     │
                     ▼
          ┌──────────────────────┐
          │ Screening Pipeline   │
          └──────────┬───────────┘
                     │
                     ▼
              Results Dashboard
```

---

# Resume Parsing

Resume parsing is implemented independently of Streamlit in:

```text
ui/resume_parser.py
```

The main interface is:

```python
extract_resume_text(...)
```

The parser dispatches based on file extension.

```text
PDF  ──┐
       │
DOCX ──┼──> Resume text
       │
TXT  ──┘
```

This functionality is intentionally separated from the UI so that it can be tested independently.

---

# LLM Architecture

The current implementation uses OpenAI models for tasks requiring natural-language interpretation.

LLM-powered components include:

### Job extraction

```text
Raw job posting
      ↓
     LLM
      ↓
Structured JobPosting
```

### Resume matching

```text
Resume + Job Requirements
            ↓
           LLM
            ↓
       ResumeMatch
```

### Cover letter generation

```text
Resume + Job + Matches
            ↓
           LLM
            ↓
       Cover Letter
```

The final fit score is calculated separately using deterministic Python code.

---

# Configuration

The application expects an OpenAI API key in `.env`.

Example:

```text
OPENAI_API_KEY=your_api_key_here
```

The `.env` file should **never be committed to Git**.

The repository's `.gitignore` excludes `.env`.

---

# Installation

## Requirements

* Python 3.14+
* Git
* An OpenAI API key

The project has primarily been developed in a Linux/WSL environment.

## Create the environment

```bash
python3 -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# Running the Application

Start the Streamlit interface:

```bash
source .venv/bin/activate
streamlit run ui/app.py
```

Open:

```text
http://localhost:8501
```

Enter a job URL, upload a resume, and select **Screen Job**.

---

# Testing

The project uses `pytest`.

Run the main deterministic/mocked test suite with:

```bash
pytest -q tests/test_scorer.py \
tests/test_scraper.py \
tests/test_extractor.py \
tests/test_matcher.py \
tests/test_cover_letter.py \
tests/test_tools.py \
tests/test_resume_parser.py \
tests/test_application_agent_graph.py
```

The current implementation has **29 relevant tests passing** across the implemented and mocked components.

Some legacy integration tests intentionally make live requests to external services:

```text
tests/test_agent.py::test_agent_runs
tests/test_graph.py::test_graph_runs
```

These tests interact with a real job URL and/or OpenAI API and are therefore not part of the deterministic test suite.

They may incur API usage and can fail due to external website or network changes.

---

# Agent Architecture

The repository contains several experimental orchestration approaches.

## Pipeline

`app/pipeline.py`

The simplest and currently most direct screening workflow.

```text
URL
 ↓
Scrape
 ↓
Extract
 ↓
Match
 ↓
Score
```

## LangGraph Screening Graph

`app/graph.py`

Provides a LangGraph representation of the screening workflow.

## Tool-Calling Agent

`app/agent.py`

Provides an OpenAI function/tool-calling implementation where the model decides which screening tools to execute.

## Application Agent

The newer application-agent components are:

```text
app/application_agent_state.py
app/application_agent_tools.py
app/application_agent_graph.py
```

This workflow is intended to operate downstream of the screening system.

Conceptually:

```text
Job Screening
      ↓
Fit Score
      ↓
Application Decision
      ↓
Evidence Retrieval
      ↓
Application Generation
```

The state schema and graph infrastructure are currently implemented and tested.

---

# Current Limitations

The project is functional but still under active development.

### Evidence retrieval

`retrieve_candidate_evidence()` currently uses a placeholder implementation.

The long-term goal is to retrieve targeted resume evidence for individual job requirements rather than passing the entire resume through the workflow.

### Application drafting agent

The newer `draft_node` remains a placeholder.

The intended future behavior is to generate application materials using the structured job requirements and retrieved candidate evidence.

### Multiple orchestration implementations

The repository currently contains three approaches to orchestrating the screening process:

* Direct pipeline
* LangGraph
* Tool-calling agent

These were developed as part of the project's experimentation with agent architectures.

A future refactor may consolidate these approaches around a single canonical architecture.

### External job-site dependencies

The scraper depends on the structure and availability of external job-posting websites.

A website redesign, bot protection, authentication requirement, or other change may prevent a posting from being retrieved correctly.

### LLM dependency

Job extraction and resume matching rely on an external LLM API and therefore:

* Require an API key
* Consume API credits
* May produce different interpretations between runs
* Depend on the availability of the API

---

# Development Roadmap

## Completed

* [x] Job posting scraper
* [x] Structured job requirement extraction
* [x] Resume-to-job matching
* [x] Deterministic fit scoring
* [x] Cover-letter generation function
* [x] LangGraph screening workflow
* [x] Tool-calling agent prototype
* [x] Application-agent state/graph foundation
* [x] PDF resume support
* [x] DOCX resume support
* [x] TXT resume support
* [x] Streamlit web interface
* [x] Requirement-level results dashboard
* [x] Automated tests for resume parsing
* [x] Tests for recent tool/state fixes

## In Progress

* [ ] Structured candidate-evidence retrieval
* [ ] Application-agent drafting
* [ ] End-to-end integration testing
* [ ] Consolidation of orchestration architectures
* [ ] Improved error handling and observability

## Planned

Potential future functionality includes:

* [ ] Save and track screened jobs
* [ ] Job/application database
* [ ] Application tracking dashboard
* [ ] Tailored cover letters
* [ ] Resume customization
* [ ] Requirement-specific evidence retrieval
* [ ] Job prioritization
* [ ] Multiple-resume support
* [ ] Search and screen multiple jobs automatically
* [ ] Job-board integrations
* [ ] Application history
* [ ] Analytics on application outcomes

---

# Design Philosophy

The project intentionally separates **LLM reasoning from deterministic application logic**.

For example:

```text
                LLM
                 │
       ┌─────────┴─────────┐
       │                   │
 Job interpretation   Resume interpretation
       │                   │
       └─────────┬─────────┘
                 │
                 ▼
           Structured data
                 │
                 ▼
          Deterministic code
                 │
                 ▼
             Fit score
```

This approach makes the system easier to:

* Test
* Debug
* Extend
* Reason about
* Replace individual components
* Compare different LLM approaches

The UI is similarly separated from the backend so that the screening pipeline can eventually be used by a CLI, API, scheduled agent, or other interface without duplicating business logic.

---

# Security

Do not commit:

* `.env`
* API keys
* Private resumes
* Personal application information
* Authentication credentials

The `.env` file is intentionally excluded from version control.

Uploaded resumes are processed by the Streamlit application and are not intentionally persisted to disk by the current UI implementation.

---

# Project Status

This project is an actively developed AI/agentic systems project focused on combining:

* Python
* LLM structured outputs
* Information extraction
* Retrieval
* Resume/job matching
* Deterministic scoring
* LangGraph
* Tool-calling agents
* Document parsing
* Web scraping
* Streamlit
* Automated testing

The current milestone is a working **job screening web application**. The next major milestone is turning the screening result into an **agentic application workflow** that can retrieve relevant candidate evidence and generate tailored application materials.
