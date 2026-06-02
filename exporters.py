"""Excel and PDF export functions."""

from __future__ import annotations

from io import BytesIO

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter


def to_excel(
    results: pd.DataFrame,
    summary: pd.DataFrame,
    improvements: pd.DataFrame,
    roadmap: pd.DataFrame,
    checklist: pd.DataFrame,
    overall_score: float,
    target_state: dict[str, str | float] | None = None,
    gap_analysis: pd.DataFrame | None = None,
    transformation_roadmap: pd.DataFrame | None = None,
    recommendations: pd.DataFrame | None = None,
    benefits: pd.DataFrame | None = None,
    investments: pd.DataFrame | None = None,
) -> bytes:
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        pd.DataFrame({"Metric": ["Weighted Overall Maturity Score"], "Value": [round(overall_score, 2)]}).to_excel(
            writer, sheet_name="Executive Summary", index=False
        )
        summary.to_excel(writer, sheet_name="Domain Summary", index=False)
        improvements.to_excel(writer, sheet_name="Top Improvements", index=False)
        roadmap.to_excel(writer, sheet_name="Roadmap", index=False)
        checklist.to_excel(writer, sheet_name="Evidence Checklist", index=False)
        results.to_excel(writer, sheet_name="Assessment Detail", index=False)
        if target_state:
            pd.DataFrame([target_state]).to_excel(writer, sheet_name="Target State", index=False)
        if gap_analysis is not None:
            gap_analysis.to_excel(writer, sheet_name="Gap Analysis", index=False)
        if transformation_roadmap is not None:
            transformation_roadmap.to_excel(writer, sheet_name="Transformation Roadmap", index=False)
        if recommendations is not None:
            recommendations.to_excel(writer, sheet_name="Recommendations", index=False)
        if benefits is not None:
            benefits.to_excel(writer, sheet_name="Benefits", index=False)
        if investments is not None:
            investments.to_excel(writer, sheet_name="Investment View", index=False)

        workbook = writer.book
        header_fill = PatternFill("solid", fgColor="1F4E78")
        header_font = Font(color="FFFFFF", bold=True)
        for worksheet in workbook.worksheets:
            worksheet.freeze_panes = "A2"
            for cell in worksheet[1]:
                cell.fill = header_fill
                cell.font = header_font
            for column_cells in worksheet.columns:
                max_length = max(len(str(cell.value or "")) for cell in column_cells)
                worksheet.column_dimensions[get_column_letter(column_cells[0].column)].width = min(max(max_length + 2, 12), 60)

    return buffer.getvalue()


def to_pdf(
    summary: pd.DataFrame,
    improvements: pd.DataFrame,
    roadmap: pd.DataFrame,
    overall_score: float,
    target_state: dict[str, str | float] | None = None,
    gap_analysis: pd.DataFrame | None = None,
    transformation_roadmap: pd.DataFrame | None = None,
    benefits: pd.DataFrame | None = None,
    investments: pd.DataFrame | None = None,
) -> bytes:
    buffer = BytesIO()
    with PdfPages(buffer) as pdf:
        fig = plt.figure(figsize=(11.69, 8.27))
        fig.suptitle("Software Quality & Delivery Transformation Scan", fontsize=20, fontweight="bold")
        fig.text(0.08, 0.82, f"Weighted overall maturity score: {overall_score:.2f} / 5", fontsize=16)
        fig.text(0.08, 0.76, "Traffic-light interpretation: Red < 2.8, Amber 2.8-3.99, Green >= 4.0", fontsize=11)
        if target_state:
            fig.text(0.08, 0.71, f"Selected target state: {target_state['Name']} ({target_state['Target Maturity']:.1f} / 5)", fontsize=12)
            fig.text(0.08, 0.67, str(target_state["Description"]), fontsize=9)
        ax = fig.add_axes([0.08, 0.16, 0.86, 0.52])
        colors = summary["Status_Color"].tolist()
        ax.barh(summary["Domain"], summary["Average_Score"], color=colors)
        ax.set_xlim(0, 5)
        ax.set_xlabel("Average score")
        ax.grid(axis="x", alpha=0.25)
        pdf.savefig(fig, bbox_inches="tight")
        plt.close(fig)

        if gap_analysis is not None:
            fig, ax = plt.subplots(figsize=(11.69, 8.27))
            ax.axis("off")
            ax.set_title("Gap Analysis", fontsize=16, fontweight="bold", pad=18)
            gap_table = gap_analysis[["Domain", "Current Score", "Target Score", "Gap", "Priority"]].copy()
            gap_table[["Current Score", "Target Score", "Gap"]] = gap_table[["Current Score", "Target Score", "Gap"]].round(2)
            table = ax.table(cellText=gap_table.values, colLabels=gap_table.columns, loc="center", cellLoc="left")
            table.auto_set_font_size(False)
            table.set_fontsize(8)
            table.scale(1, 1.6)
            pdf.savefig(fig, bbox_inches="tight")
            plt.close(fig)

        fig, ax = plt.subplots(figsize=(11.69, 8.27))
        ax.axis("off")
        ax.set_title("Top 5 Improvement Areas", fontsize=16, fontweight="bold", pad=18)
        table_data = improvements[["Domain", "Question ID", "Score", "Question"]].copy()
        table_data["Question"] = table_data["Question"].str.wrap(70)
        table = ax.table(cellText=table_data.values, colLabels=table_data.columns, loc="center", cellLoc="left")
        table.auto_set_font_size(False)
        table.set_fontsize(8)
        table.scale(1, 1.8)
        pdf.savefig(fig, bbox_inches="tight")
        plt.close(fig)

        fig, ax = plt.subplots(figsize=(11.69, 8.27))
        ax.axis("off")
        ax.set_title("Roadmap", fontsize=16, fontweight="bold", pad=18)
        roadmap_table = roadmap[["Horizon", "Domain", "Current Score", "Recommended Action"]].head(8).copy()
        roadmap_table["Recommended Action"] = roadmap_table["Recommended Action"].str.wrap(55)
        table = ax.table(cellText=roadmap_table.values, colLabels=roadmap_table.columns, loc="center", cellLoc="left")
        table.auto_set_font_size(False)
        table.set_fontsize(8)
        table.scale(1, 1.9)
        pdf.savefig(fig, bbox_inches="tight")
        plt.close(fig)

        if transformation_roadmap is not None and not transformation_roadmap.empty:
            fig, ax = plt.subplots(figsize=(11.69, 8.27))
            ax.axis("off")
            ax.set_title("Transformation Roadmap", fontsize=16, fontweight="bold", pad=18)
            transform_table = transformation_roadmap[["Wave", "Domain", "Title", "Effort", "Business Value", "Priority"]].head(12).copy()
            transform_table["Title"] = transform_table["Title"].str.wrap(38)
            table = ax.table(cellText=transform_table.values, colLabels=transform_table.columns, loc="center", cellLoc="left")
            table.auto_set_font_size(False)
            table.set_fontsize(7)
            table.scale(1, 1.7)
            pdf.savefig(fig, bbox_inches="tight")
            plt.close(fig)

        if benefits is not None:
            fig, ax = plt.subplots(figsize=(11.69, 8.27))
            ax.axis("off")
            ax.set_title("Benefits Overview", fontsize=16, fontweight="bold", pad=18)
            table = ax.table(cellText=benefits.values, colLabels=benefits.columns, loc="center", cellLoc="left")
            table.auto_set_font_size(False)
            table.set_fontsize(8)
            table.scale(1, 1.6)
            pdf.savefig(fig, bbox_inches="tight")
            plt.close(fig)

        if investments is not None:
            fig, ax = plt.subplots(figsize=(11.69, 8.27))
            ax.axis("off")
            ax.set_title("Investment View", fontsize=16, fontweight="bold", pad=18)
            table = ax.table(cellText=investments.values, colLabels=investments.columns, loc="center", cellLoc="left")
            table.auto_set_font_size(False)
            table.set_fontsize(8)
            table.scale(1, 1.6)
            pdf.savefig(fig, bbox_inches="tight")
            plt.close(fig)

    return buffer.getvalue()
