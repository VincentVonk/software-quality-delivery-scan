"""Streamlit app for a Software Quality & Delivery Capability Scan."""

from __future__ import annotations

import matplotlib.pyplot as plt
import streamlit as st

from exporters import to_excel, to_pdf
from scan_config import DOMAINS, SCORE_LABELS
from scoring import (
    build_results_frame,
    default_notes,
    default_scores,
    domain_summary,
    evidence_checklist,
    roadmap_for,
    top_improvement_areas,
    weighted_overall_score,
)


st.set_page_config(
    page_title="Software Quality & Delivery Capability Scan",
    layout="wide",
)


def initialize_state() -> None:
    if "scores" not in st.session_state:
        st.session_state.scores = default_scores()
    if "notes" not in st.session_state:
        st.session_state.notes = default_notes()
    if "client_name" not in st.session_state:
        st.session_state.client_name = ""
    if "assessment_date" not in st.session_state:
        st.session_state.assessment_date = ""
    if "consultant" not in st.session_state:
        st.session_state.consultant = ""


def compute_outputs():
    results = build_results_frame(st.session_state.scores, st.session_state.notes)
    summary = domain_summary(results)
    overall = weighted_overall_score(summary)
    improvements = top_improvement_areas(results)
    roadmap = roadmap_for(summary, improvements)
    checklist = evidence_checklist(results)
    return results, summary, overall, improvements, roadmap, checklist


def render_sidebar(results, summary, overall, improvements, roadmap, checklist) -> None:
    st.sidebar.header("Assessment")
    st.sidebar.text_input("Client name", key="client_name")
    st.sidebar.text_input("Consultant", key="consultant")
    st.sidebar.text_input("Assessment date", key="assessment_date", placeholder="YYYY-MM-DD")
    st.sidebar.metric("Overall maturity", f"{overall:.2f} / 5")

    excel_bytes = to_excel(results, summary, improvements, roadmap, checklist, overall)
    pdf_bytes = to_pdf(summary, improvements, roadmap, overall)
    st.sidebar.download_button(
        "Export Excel",
        data=excel_bytes,
        file_name="software_quality_capability_scan.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )
    st.sidebar.download_button(
        "Export PDF",
        data=pdf_bytes,
        file_name="software_quality_capability_scan.pdf",
        mime="application/pdf",
        use_container_width=True,
    )


def score_help(score: int) -> str:
    return f"{score} = {SCORE_LABELS[score]}"


def dashboard_page(summary, overall, improvements) -> None:
    st.title("Software Quality & Delivery Capability Scan")
    st.caption("Assess delivery maturity, quality controls, automation, evidence, and improvement priorities.")

    metric_cols = st.columns(4)
    metric_cols[0].metric("Weighted overall score", f"{overall:.2f} / 5")
    metric_cols[1].metric("Green domains", int((summary["Traffic_Light"] == "Green").sum()))
    metric_cols[2].metric("Amber domains", int((summary["Traffic_Light"] == "Amber").sum()))
    metric_cols[3].metric("Red domains", int((summary["Traffic_Light"] == "Red").sum()))

    left, right = st.columns([1.3, 1])
    with left:
        st.subheader("Domain maturity")
        fig, ax = plt.subplots(figsize=(9, 4.8))
        plot_summary = summary.sort_values("Average_Score")
        ax.barh(plot_summary["Domain"], plot_summary["Average_Score"], color=plot_summary["Status_Color"])
        ax.set_xlim(0, 5)
        ax.set_xlabel("Average score")
        ax.grid(axis="x", alpha=0.25)
        st.pyplot(fig, use_container_width=True)

    with right:
        st.subheader("Traffic-light status")
        status_view = summary[["Domain", "Average_Score", "Traffic_Light"]].copy()
        status_view["Average_Score"] = status_view["Average_Score"].round(2)
        st.dataframe(status_view, use_container_width=True, hide_index=True)

    st.subheader("Top 5 improvement areas")
    priority_view = improvements[["Domain", "Question ID", "Score", "Question", "Evidence Expected"]].copy()
    st.dataframe(priority_view, use_container_width=True, hide_index=True)


def assessment_page() -> None:
    st.title("Assessment Input")
    st.caption("Score each question from 1 to 5 and capture concise evidence notes.")

    labels = [score_help(score) for score in SCORE_LABELS]
    for domain in DOMAINS:
        with st.expander(f"{domain.name} | Weight {domain.weight:.0%}", expanded=True):
            for question in domain.questions:
                cols = st.columns([1.5, 4, 2, 3])
                cols[0].markdown(f"**{question.id}**")
                cols[1].write(question.text)
                selected = cols[2].select_slider(
                    "Score",
                    options=list(SCORE_LABELS.keys()),
                    value=st.session_state.scores.get(question.id, 3),
                    format_func=lambda value: f"{value}",
                    key=f"score_{question.id}",
                    label_visibility="collapsed",
                    help=" | ".join(labels),
                )
                st.session_state.scores[question.id] = selected
                note = cols[3].text_input(
                    "Evidence notes",
                    value=st.session_state.notes.get(question.id, ""),
                    key=f"note_{question.id}",
                    placeholder=question.evidence,
                    label_visibility="collapsed",
                )
                st.session_state.notes[question.id] = note


def roadmap_page(roadmap) -> None:
    st.title("Roadmap")
    st.caption("Prioritized actions based on the largest weighted maturity gaps.")
    horizon_order = ["0-90 days", "3-6 months", "6-12 months"]
    for horizon in horizon_order:
        items = roadmap[roadmap["Horizon"] == horizon]
        if not items.empty:
            st.subheader(horizon)
            st.dataframe(items.drop(columns=["Horizon"]), use_container_width=True, hide_index=True)


def evidence_page(checklist) -> None:
    st.title("Evidence Checklist")
    st.caption("Use this checklist to plan document requests, interviews, and system walkthroughs.")
    status_filter = st.multiselect(
        "Evidence status",
        options=sorted(checklist["Evidence Status"].unique()),
        default=sorted(checklist["Evidence Status"].unique()),
    )
    filtered = checklist[checklist["Evidence Status"].isin(status_filter)]
    st.dataframe(filtered, use_container_width=True, hide_index=True)


def main() -> None:
    initialize_state()
    results, summary, overall, improvements, roadmap, checklist = compute_outputs()
    render_sidebar(results, summary, overall, improvements, roadmap, checklist)

    selected_page = st.sidebar.radio(
        "Page",
        ["Dashboard", "Assessment Input", "Roadmap", "Evidence Checklist"],
    )
    if selected_page == "Dashboard":
        dashboard_page(summary, overall, improvements)
    elif selected_page == "Assessment Input":
        assessment_page()
    elif selected_page == "Roadmap":
        roadmap_page(roadmap)
    else:
        evidence_page(checklist)


if __name__ == "__main__":
    main()
