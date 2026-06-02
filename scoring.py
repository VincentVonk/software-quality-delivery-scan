"""Scoring and recommendation helpers."""

from __future__ import annotations

import pandas as pd

from scan_config import DOMAINS, STATUS_RULES


def default_scores() -> dict[str, int]:
    return {question.id: 3 for domain in DOMAINS for question in domain.questions}


def default_notes() -> dict[str, str]:
    return {question.id: "" for domain in DOMAINS for question in domain.questions}


def build_results_frame(scores: dict[str, int], notes: dict[str, str]) -> pd.DataFrame:
    rows = []
    for domain in DOMAINS:
        for question in domain.questions:
            score = int(scores.get(question.id, 3))
            rows.append(
                {
                    "Domain": domain.name,
                    "Weight": domain.weight,
                    "Question ID": question.id,
                    "Question": question.text,
                    "Score": score,
                    "Evidence Expected": question.evidence,
                    "Evidence Notes": notes.get(question.id, ""),
                }
            )
    return pd.DataFrame(rows)


def domain_summary(results: pd.DataFrame) -> pd.DataFrame:
    summary = (
        results.groupby("Domain", as_index=False)
        .agg(Average_Score=("Score", "mean"), Weight=("Weight", "first"), Questions=("Question ID", "count"))
        .sort_values("Domain")
    )
    summary["Weighted_Contribution"] = summary["Average_Score"] * summary["Weight"]
    summary[["Traffic_Light", "Status_Color"]] = summary["Average_Score"].apply(lambda value: pd.Series(status_for_score(value)))
    return summary


def weighted_overall_score(summary: pd.DataFrame) -> float:
    total_weight = summary["Weight"].sum()
    if total_weight == 0:
        return 0.0
    return float(summary["Weighted_Contribution"].sum() / total_weight)


def status_for_score(score: float) -> tuple[str, str]:
    for threshold, label, color in STATUS_RULES:
        if score >= threshold:
            return label, color
    return "Red", "#c62828"


def top_improvement_areas(results: pd.DataFrame, limit: int = 5) -> pd.DataFrame:
    priority = results.copy()
    priority["Gap_To_Target"] = 5 - priority["Score"]
    priority["Priority_Score"] = priority["Gap_To_Target"] * priority["Weight"]
    priority = priority.sort_values(["Priority_Score", "Score", "Domain"], ascending=[False, True, True])
    return priority.head(limit).reset_index(drop=True)


def roadmap_for(summary: pd.DataFrame, improvements: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, item in improvements.iterrows():
        score = int(item["Score"])
        if score <= 2:
            horizon = "0-90 days"
            action = "Stabilize the practice, define ownership, and create minimum delivery controls."
        elif score == 3:
            horizon = "3-6 months"
            action = "Standardize execution, add measurement, and embed the practice into governance routines."
        else:
            horizon = "6-12 months"
            action = "Optimize through automation, trend analysis, and continuous improvement loops."
        rows.append(
            {
                "Horizon": horizon,
                "Domain": item["Domain"],
                "Improvement Area": item["Question"],
                "Current Score": score,
                "Recommended Action": action,
                "Evidence to Build": item["Evidence Expected"],
            }
        )

    weak_domains = summary[summary["Average_Score"] < 2.8].sort_values("Average_Score")
    for _, domain in weak_domains.iterrows():
        rows.append(
            {
                "Horizon": "0-90 days",
                "Domain": domain["Domain"],
                "Improvement Area": "Domain-level operating model",
                "Current Score": round(float(domain["Average_Score"]), 2),
                "Recommended Action": "Create a focused recovery plan with named owners, target metrics, and governance checkpoints.",
                "Evidence to Build": "Recovery backlog, owner map, weekly metric review",
            }
        )

    return pd.DataFrame(rows)


def evidence_checklist(results: pd.DataFrame) -> pd.DataFrame:
    checklist = results[["Domain", "Question ID", "Evidence Expected", "Evidence Notes", "Score"]].copy()
    checklist["Evidence Status"] = checklist.apply(
        lambda row: "Collected" if str(row["Evidence Notes"]).strip() else ("Needed urgently" if row["Score"] <= 2 else "Needed"),
        axis=1,
    )
    return checklist
