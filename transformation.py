"""Transformation roadmap calculations for AS-IS to TO-BE planning."""

from __future__ import annotations

import pandas as pd

from roadmap_config import BENEFIT_CATEGORIES, RECOMMENDATIONS, TARGET_STATES


EFFORT_SCORE = {"Low": 1, "Medium": 2, "High": 3}
VALUE_SCORE = {"Low": 1, "Medium": 2, "High": 3}
PRIORITY_SCORE = {"High": 1, "Medium": 2, "Low": 3}
WAVE_SCORE = {"0-3 months": 1, "3-6 months": 2, "6-12 months": 3, "12+ months": 4}


def determine_priority(gap: float) -> str:
    if gap >= 2.0:
        return "High"
    if gap >= 1.0:
        return "Medium"
    return "Low"


def calculate_gap_analysis(summary: pd.DataFrame, target_state_name: str) -> pd.DataFrame:
    target = TARGET_STATES[target_state_name]["target_maturity"]
    gap = summary[["Domain", "Average_Score", "Traffic_Light", "Weight"]].copy()
    gap = gap.rename(columns={"Average_Score": "Current Score", "Traffic_Light": "Traffic Light"})
    gap["Target Score"] = target
    gap["Gap"] = (gap["Target Score"] - gap["Current Score"]).clip(lower=0)
    gap["Priority"] = gap["Gap"].apply(determine_priority)
    gap["Risk Score"] = gap["Gap"] * gap["Weight"]
    gap["Sort Priority"] = gap["Priority"].map(PRIORITY_SCORE)
    gap = gap.sort_values(["Sort Priority", "Risk Score", "Gap"], ascending=[True, False, False])
    return gap.drop(columns=["Sort Priority"]).reset_index(drop=True)


def highest_risk_domains(gap_analysis: pd.DataFrame, limit: int = 3) -> pd.DataFrame:
    return gap_analysis.sort_values(["Risk Score", "Gap"], ascending=[False, False]).head(limit).reset_index(drop=True)


def lowest_scoring_domains(summary: pd.DataFrame, limit: int = 3) -> pd.DataFrame:
    return summary.sort_values("Average_Score").head(limit).reset_index(drop=True)


def generate_roadmap(gap_analysis: pd.DataFrame) -> pd.DataFrame:
    relevant_domains = gap_analysis[gap_analysis["Gap"] > 0]
    if relevant_domains.empty:
        relevant_domains = gap_analysis.nsmallest(3, "Current Score")

    rows = []
    for recommendation in RECOMMENDATIONS:
        match = relevant_domains[relevant_domains["Domain"] == recommendation["domain"]]
        if match.empty:
            continue

        domain_gap = match.iloc[0]
        row = {
            "Wave": recommendation["wave"],
            "Domain": recommendation["domain"],
            "Title": recommendation["title"],
            "Description": recommendation["description"],
            "Effort": recommendation["effort"],
            "Business Value": recommendation["business_value"],
            "Dependency": recommendation["dependency"],
            "Expected Benefit": recommendation["expected_benefit"],
            "CGI Service Opportunity": recommendation["cgi_service_opportunity"],
            "Priority": domain_gap["Priority"],
            "Gap": round(float(domain_gap["Gap"]), 2),
            "Suggested Timing": recommendation["wave"],
        }
        rows.append(row)

    roadmap = pd.DataFrame(rows)
    if roadmap.empty:
        return roadmap
    roadmap["Investment Classification"] = roadmap.apply(classify_investment, axis=1)
    roadmap["Sort Effort"] = roadmap["Effort"].map(EFFORT_SCORE)
    roadmap["Sort Value"] = roadmap["Business Value"].map(VALUE_SCORE)
    roadmap["Sort Priority"] = roadmap["Priority"].map(PRIORITY_SCORE)
    roadmap["Sort Wave"] = roadmap["Wave"].map(WAVE_SCORE)
    roadmap = roadmap.sort_values(["Sort Wave", "Sort Priority", "Sort Value", "Sort Effort"], ascending=[True, True, False, True])
    return roadmap.drop(columns=["Sort Effort", "Sort Value", "Sort Priority", "Sort Wave"]).reset_index(drop=True)


def classify_investment(item: pd.Series | dict[str, str]) -> str:
    effort = item["Effort"]
    value = item["Business Value"]
    if effort == "Low" and value == "High":
        return "Quick wins"
    if effort == "High" and value == "High":
        return "Strategic initiatives"
    if effort == "Low" and value == "Medium":
        return "Nice to have"
    if effort == "High" and value == "Low":
        return "Deprioritize"
    return "Balanced initiatives"


def generate_benefits_summary(roadmap: pd.DataFrame) -> pd.DataFrame:
    recommendation_lookup = {item["title"]: item for item in RECOMMENDATIONS}
    benefit_scores = {category: 0 for category in BENEFIT_CATEGORIES}

    for _, item in roadmap.iterrows():
        recommendation = recommendation_lookup.get(item["Title"])
        if not recommendation:
            continue
        value_score = VALUE_SCORE.get(item["Business Value"], 1)
        priority_boost = {"High": 2, "Medium": 1, "Low": 0}.get(item["Priority"], 0)
        for benefit in recommendation["benefits"]:
            benefit_scores[benefit] += value_score + priority_boost

    rows = []
    for category, score in benefit_scores.items():
        if score >= 6:
            level = "High"
        elif score >= 3:
            level = "Medium"
        elif score > 0:
            level = "Low"
        else:
            level = "Low"
        rows.append({"Benefit Category": category, "Qualitative Benefit": level})
    return pd.DataFrame(rows)


def investment_view(roadmap: pd.DataFrame) -> pd.DataFrame:
    categories = {
        "Quick wins": "Low effort / High value",
        "Strategic initiatives": "High effort / High value",
        "Nice to have": "Low effort / Medium value",
        "Deprioritize": "High effort / Low value",
    }
    rows = []
    for category, definition in categories.items():
        matches = roadmap[roadmap["Investment Classification"] == category] if not roadmap.empty else pd.DataFrame()
        rows.append(
            {
                "Investment Classification": category,
                "Definition": definition,
                "Items": len(matches),
                "Roadmap Items": ", ".join(matches["Title"].tolist()) if not matches.empty else "",
            }
        )
    return pd.DataFrame(rows)
