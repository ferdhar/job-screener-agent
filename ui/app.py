import sys
from pathlib import Path

# Streamlit inserts the entry script's own directory (ui/) at the front of
# sys.path before executing it. Since ui/ contains a file named app.py,
# `import app` would otherwise resolve to that file instead of the real
# `app` backend package at the project root. Put the project root ahead
# of it so the real package is found first.
PROJECT_ROOT = str(Path(__file__).resolve().parent.parent)

# Force it to the front rather than just checking membership: it may
# already be on sys.path (e.g. via pytest) but after ui/, which would
# still leave ui/app.py shadowing the real package.
sys.path = [PROJECT_ROOT] + [p for p in sys.path if p != PROJECT_ROOT]

import streamlit as st

from app.pipeline import screen_job
from ui.resume_parser import UnsupportedResumeFormat, extract_resume_text

STATUS_ICONS = {
    "matched": "✅",
    "partial": "🟡",
    "missing": "❌",
}


def render_score_summary(score: dict) -> None:
    overall_col, required_col, preferred_col = st.columns(3)

    overall_col.metric("Overall Fit", f"{score['overall_score']:.0f} / 100")
    overall_col.progress(min(max(score["overall_score"], 0), 100) / 100)

    required_col.metric("Required Skills", f"{score['required_score']:.0f} / 100")
    required_col.progress(min(max(score["required_score"], 0), 100) / 100)

    preferred_col.metric("Preferred Skills", f"{score['preferred_score']:.0f} / 100")
    preferred_col.progress(min(max(score["preferred_score"], 0), 100) / 100)


def render_recommendation(overall_score: float) -> None:
    if overall_score >= 75:
        st.success(
            "**Strong fit** — this candidate closely matches the role's requirements."
        )
    elif overall_score >= 50:
        st.warning(
            "**Moderate fit** — some requirement gaps exist; "
            "consider a tailored application."
        )
    else:
        st.error(
            "**Weak fit** — significant gaps against the role's requirements."
        )


def render_requirement_group(requirements, match_by_id, label: str) -> None:
    st.markdown(f"#### {label}")

    if not requirements:
        st.caption("None listed in the job posting.")
        return

    for requirement in requirements:
        result = match_by_id.get(requirement.id)
        icon = STATUS_ICONS.get(result.status, "❔") if result else "❔"

        with st.expander(f"{icon}  {requirement.description}"):
            st.caption(f"Category: {requirement.category.replace('_', ' ').title()}")

            if result is None:
                st.warning(
                    "No match data was returned for this requirement."
                )
                continue

            st.markdown(f"**Status:** {result.status.title()}")
            st.markdown(
                f"**Evidence:** {result.evidence or '_No evidence provided._'}"
            )


def render_results(result: dict) -> None:
    job = result["job"]
    match = result["match"]
    score = result["score"]

    st.header(job.title or "Untitled Role")

    subtitle_parts = [part for part in (job.company, job.location) if part]

    if subtitle_parts:
        st.caption(" · ".join(subtitle_parts))

    render_recommendation(score["overall_score"])

    st.subheader("Fit Score")
    render_score_summary(score)

    st.subheader("Requirement Matching")

    match_by_id = {
        item.requirement_id: item for item in match.requirement_matches
    }

    required_requirements = [
        requirement
        for requirement in job.requirements
        if requirement.importance == "required"
    ]
    preferred_requirements = [
        requirement
        for requirement in job.requirements
        if requirement.importance == "preferred"
    ]

    render_requirement_group(required_requirements, match_by_id, "Required")
    render_requirement_group(preferred_requirements, match_by_id, "Preferred")

    st.subheader("Strengths & Gaps")
    strengths_col, gaps_col = st.columns(2)

    with strengths_col:
        st.markdown("**Strengths**")

        if match.strengths:
            for strength in match.strengths:
                st.markdown(f"- {strength}")
        else:
            st.caption("No specific strengths identified.")

    with gaps_col:
        st.markdown("**Gaps**")

        if match.gaps:
            for gap in match.gaps:
                st.markdown(f"- {gap}")
        else:
            st.caption("No specific gaps identified.")


def run_screening(job_url: str, uploaded_resume) -> None:
    st.session_state.pop("screening_result", None)
    st.session_state.pop("screening_error", None)

    if not job_url:
        st.session_state["screening_error"] = "Enter a job posting URL."
        return

    if uploaded_resume is None:
        st.session_state["screening_error"] = (
            "Upload a resume (PDF, DOCX, or TXT)."
        )
        return

    try:
        resume_text = extract_resume_text(
            uploaded_resume.name,
            uploaded_resume.getvalue(),
        )
    except (UnsupportedResumeFormat, ValueError) as exc:
        st.session_state["screening_error"] = str(exc)
        return

    try:
        with st.spinner(
            "Fetching the job posting, extracting requirements, and "
            "matching your resume... this can take a minute."
        ):
            result = screen_job(
                job_url,
                resume_text,
                generate_letter=False,
            )
    except Exception as exc:
        st.session_state["screening_error"] = f"Screening failed: {exc}"
        return

    st.session_state["screening_result"] = result


def main() -> None:
    st.set_page_config(
        page_title="Job Fit Screener",
        page_icon="🧭",
        layout="wide",
    )

    st.title("🧭 Job Fit Screener")
    st.write(
        "Paste a job posting URL and upload a resume to get a "
        "requirement-by-requirement fit assessment."
    )

    job_url = st.text_input(
        "Job posting URL",
        placeholder="https://company.com/careers/job-id",
    )

    uploaded_resume = st.file_uploader(
        "Resume",
        type=["pdf", "docx", "txt"],
    )

    if st.button("Screen Job", type="primary"):
        run_screening(job_url, uploaded_resume)

    error = st.session_state.get("screening_error")

    if error:
        st.error(error)

    result = st.session_state.get("screening_result")

    if result:
        st.divider()
        render_results(result)


if __name__ == "__main__":
    main()
