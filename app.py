"""Streamlit app for a Software Quality & Delivery Transformation Scan."""

from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from exporters import to_excel, to_pdf
from roadmap_config import RECOMMENDATIONS, TARGET_STATES, WAVES
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
from transformation import (
    calculate_gap_analysis,
    generate_benefits_summary,
    generate_roadmap,
    highest_risk_domains,
    investment_view,
    lowest_scoring_domains,
)


st.set_page_config(
    page_title="Software Quality & Delivery Transformation Scan",
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
    if "target_state" not in st.session_state:
        st.session_state.target_state = "Professional Delivery"


def compute_outputs():
    results = build_results_frame(st.session_state.scores, st.session_state.notes)
    summary = domain_summary(results)
    overall = weighted_overall_score(summary)
    improvements = top_improvement_areas(results)
    roadmap = roadmap_for(summary, improvements)
    checklist = evidence_checklist(results)
    gap_analysis = calculate_gap_analysis(summary, st.session_state.target_state)
    transformation_roadmap = generate_roadmap(gap_analysis)
    benefits = generate_benefits_summary(transformation_roadmap)
    investments = investment_view(transformation_roadmap)
    return results, summary, overall, improvements, roadmap, checklist, gap_analysis, transformation_roadmap, benefits, investments


def selected_target_state() -> dict[str, str | float]:
    target = TARGET_STATES[st.session_state.target_state]
    return {
        "Name": st.session_state.target_state,
        "Description": target["description"],
        "Target Maturity": target["target_maturity"],
    }


def recommendation_table() -> pd.DataFrame:
    rows = []
    for recommendation in RECOMMENDATIONS:
        item = dict(recommendation)
        item["benefits"] = ", ".join(item["benefits"])
        rows.append(item)
    return pd.DataFrame(rows)


def render_sidebar(
    results,
    summary,
    overall,
    improvements,
    roadmap,
    checklist,
    gap_analysis,
    transformation_roadmap,
    benefits,
    investments,
) -> None:
    st.sidebar.header("Assessment")
    st.sidebar.text_input("Client name", key="client_name")
    st.sidebar.text_input("Consultant", key="consultant")
    st.sidebar.text_input("Assessment date", key="assessment_date", placeholder="YYYY-MM-DD")
    st.sidebar.metric("Overall maturity", f"{overall:.2f} / 5")

    excel_bytes = to_excel(
        results,
        summary,
        improvements,
        roadmap,
        checklist,
        overall,
        selected_target_state(),
        gap_analysis,
        transformation_roadmap,
        recommendation_table(),
        benefits,
        investments,
    )
    pdf_bytes = to_pdf(
        summary,
        improvements,
        roadmap,
        overall,
        selected_target_state(),
        gap_analysis,
        transformation_roadmap,
        benefits,
        investments,
    )
    st.sidebar.download_button(
        "Export Excel",
        data=excel_bytes,
        file_name="software_quality_delivery_transformation_scan.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )
    st.sidebar.download_button(
        "Export PDF",
        data=pdf_bytes,
        file_name="software_quality_delivery_transformation_scan.pdf",
        mime="application/pdf",
        use_container_width=True,
    )


def score_help(score: int) -> str:
    return f"{score} = {SCORE_LABELS[score]}"


def dashboard_page(summary, overall, improvements) -> None:
    st.title("Software Quality & Delivery Transformation Scan")
    st.caption("Assess current maturity, identify gaps, and shape a practical transformation roadmap from AS-IS to TO-BE.")

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


def transformation_page(summary, overall, gap_analysis, transformation_roadmap, benefits, investments) -> None:
    st.title("Transformation Roadmap")
    st.caption("Use the current assessment as the AS-IS view, select the ambition level, and generate a TO-BE roadmap.")

    target_names = list(TARGET_STATES.keys())
    st.selectbox(
        "Target state ambition",
        options=target_names,
        index=target_names.index(st.session_state.target_state),
        key="target_state",
        help="Select the desired maturity ambition for the transformation roadmap.",
    )
    target = selected_target_state()
    st.info(f"{target['Description']} Target maturity: {target['Target Maturity']:.1f} / 5")

    as_is, risks = st.columns(2)
    with as_is:
        st.subheader("AS-IS overview")
        st.metric("Overall maturity score", f"{overall:.2f} / 5")
        domain_view = summary[["Domain", "Average_Score", "Traffic_Light"]].copy()
        domain_view["Average_Score"] = domain_view["Average_Score"].round(2)
        st.dataframe(domain_view, use_container_width=True, hide_index=True)
    with risks:
        st.subheader("Risk focus")
        low_domains = lowest_scoring_domains(summary)
        risk_domains = highest_risk_domains(gap_analysis)
        st.write("Lowest scoring domains")
        st.dataframe(low_domains[["Domain", "Average_Score", "Traffic_Light"]], use_container_width=True, hide_index=True)
        st.write("Highest risk domains")
        st.dataframe(risk_domains[["Domain", "Gap", "Priority", "Risk Score"]], use_container_width=True, hide_index=True)

    st.subheader("Gap analysis")
    gap_view = gap_analysis[["Domain", "Current Score", "Target Score", "Gap", "Priority"]].copy()
    gap_view[["Current Score", "Target Score", "Gap"]] = gap_view[["Current Score", "Target Score", "Gap"]].round(2)
    st.dataframe(gap_view, use_container_width=True, hide_index=True)

    tab_roadmap, tab_benefits, tab_investment, tab_library = st.tabs(
        ["Roadmap", "Benefits", "Investment View", "Recommendation Library"]
    )
    with tab_roadmap:
        for wave_key, wave in WAVES.items():
            wave_items = transformation_roadmap[transformation_roadmap["Wave"] == wave_key]
            st.subheader(wave["name"])
            st.caption(wave["focus"])
            if wave_items.empty:
                st.write("No recommendations selected for this wave based on the current gaps.")
            else:
                st.dataframe(
                    wave_items[
                        [
                            "Domain",
                            "Title",
                            "Description",
                            "Effort",
                            "Business Value",
                            "Priority",
                            "Dependency",
                            "Expected Benefit",
                            "CGI Service Opportunity",
                        ]
                    ],
                    use_container_width=True,
                    hide_index=True,
                )
    with tab_benefits:
        st.dataframe(benefits, use_container_width=True, hide_index=True)
    with tab_investment:
        investment_detail = transformation_roadmap[
            ["Title", "Domain", "Effort", "Business Value", "Priority", "Suggested Timing", "Investment Classification"]
        ]
        st.dataframe(investment_detail, use_container_width=True, hide_index=True)
        st.write("Investment matrix")
        st.dataframe(investments, use_container_width=True, hide_index=True)
    with tab_library:
        st.dataframe(recommendation_table(), use_container_width=True, hide_index=True)


def export_page(
    results,
    summary,
    overall,
    improvements,
    roadmap,
    checklist,
    gap_analysis,
    transformation_roadmap,
    benefits,
    investments,
) -> None:
    st.title("Export")
    st.caption("Download client-ready outputs including assessment detail and transformation planning views.")
    target = selected_target_state()
    st.write(f"Selected target state: **{target['Name']}** ({target['Target Maturity']:.1f} / 5)")

    excel_bytes = to_excel(
        results,
        summary,
        improvements,
        roadmap,
        checklist,
        overall,
        target,
        gap_analysis,
        transformation_roadmap,
        recommendation_table(),
        benefits,
        investments,
    )
    pdf_bytes = to_pdf(summary, improvements, roadmap, overall, target, gap_analysis, transformation_roadmap, benefits, investments)
    cols = st.columns(2)
    cols[0].download_button(
        "Export Excel",
        data=excel_bytes,
        file_name="software_quality_delivery_transformation_scan.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )
    cols[1].download_button(
        "Export PDF",
        data=pdf_bytes,
        file_name="software_quality_delivery_transformation_scan.pdf",
        mime="application/pdf",
        use_container_width=True,
    )


def main() -> None:
    initialize_state()
    (
        results,
        summary,
        overall,
        improvements,
        roadmap,
        checklist,
        gap_analysis,
        transformation_roadmap,
        benefits,
        investments,
    ) = compute_outputs()
    render_sidebar(results, summary, overall, improvements, roadmap, checklist, gap_analysis, transformation_roadmap, benefits, investments)

    selected_page = st.sidebar.radio(
        "Page",
        ["Dashboard", "Assessment Input", "Roadmap", "Evidence Checklist", "Transformation Roadmap", "Export"],
    )
    if selected_page == "Dashboard":
        dashboard_page(summary, overall, improvements)
    elif selected_page == "Assessment Input":
        assessment_page()
    elif selected_page == "Roadmap":
        roadmap_page(roadmap)
    elif selected_page == "Evidence Checklist":
        evidence_page(checklist)
    elif selected_page == "Transformation Roadmap":
        transformation_page(summary, overall, gap_analysis, transformation_roadmap, benefits, investments)
    else:
        export_page(results, summary, overall, improvements, roadmap, checklist, gap_analysis, transformation_roadmap, benefits, investments)


if __name__ == "__main__":
    main()
