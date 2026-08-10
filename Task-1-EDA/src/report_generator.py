"""
report_generator.py
----------------------
Compiles all EDA findings (structural overview, missing values, duplicates,
outliers, hypothesis tests, insights) into a professional report available
in three formats:

    - Markdown (.md)  - lightweight, renders nicely on GitHub.
    - PDF (.pdf)       - polished, presentation-ready deliverable.
    - Excel (.xlsx)    - every table as its own sheet, for further analysis.

The generator keeps a single internal list of structured sections
(`self.sections`), so all three export formats stay in sync automatically -
add a section once, and it shows up everywhere.
"""

import os
from datetime import datetime

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak,
)

from src.logger_config import get_logger

logger = get_logger(__name__)


class ReportGenerator:
    """Builds a consolidated EDA report and exports it to Markdown, PDF, and Excel."""

    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.title = "EDA Report"
        self.sections = []  # list of dicts: {type, heading, content}

    # ------------------------------------------------------------------
    # Content builders (format-agnostic)
    # ------------------------------------------------------------------
    def add_title(self, title: str):
        self.title = title
        self.sections.append({"type": "title", "heading": title,
                               "content": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})

    def add_section(self, heading: str, content: str):
        self.sections.append({"type": "text", "heading": heading, "content": content})

    def add_dataframe(self, heading: str, df: pd.DataFrame):
        self.sections.append({"type": "table", "heading": heading, "content": df})

    def add_dict_as_table(self, heading: str, data: dict, col_names=("Metric", "Value")):
        # Format values as display strings up front so a mixed int/float dict
        # (e.g. row count + memory usage) doesn't get silently upcast to
        # float by pandas when it builds the DataFrame column.
        formatted = [(k, f"{v:,}" if isinstance(v, int) else v) for k, v in data.items()]
        df = pd.DataFrame(formatted, columns=list(col_names))
        self.sections.append({"type": "table", "heading": heading, "content": df})

    def add_hypothesis_results(self, results: list):
        text_lines = []
        for r in results:
            text_lines.append(
                f"**{r['test_name']}**  \n"
                f"Statistic: `{r['statistic']}` | p-value: `{r['p_value']}` | "
                f"alpha: `{r['alpha']}`  \nConclusion: **{r['conclusion']}**"
            )
        self.sections.append({
            "type": "text", "heading": "Hypothesis Test Results",
            "content": "\n\n".join(text_lines)
        })

    def add_insights(self, heading: str, insights: list):
        content = "\n".join([f"- {insight}" for insight in insights])
        self.sections.append({"type": "text", "heading": heading, "content": content})

    def add_images(self, heading: str, image_paths: list):
        self.sections.append({"type": "images", "heading": heading,
                               "content": [p for p in image_paths if p]})

    # ------------------------------------------------------------------
    # Markdown export
    # ------------------------------------------------------------------
    def save(self, filename: str = "eda_report.md") -> str:
        """Save the report as Markdown (default, backward-compatible entry point)."""
        return self.save_markdown(filename)

    def save_markdown(self, filename: str = "eda_report.md") -> str:
        lines = []
        for section in self.sections:
            if section["type"] == "title":
                lines.append(f"# {section['heading']}\n")
                lines.append(f"_Generated on {section['content']}_\n")
            elif section["type"] == "text":
                lines.append(f"\n## {section['heading']}\n")
                lines.append(section["content"])
            elif section["type"] == "table":
                lines.append(f"\n## {section['heading']}\n")
                lines.append(section["content"].to_markdown())
            elif section["type"] == "images":
                lines.append(f"\n## {section['heading']}\n")
                for path in section["content"]:
                    filename_only = os.path.basename(path)
                    lines.append(f"![{filename_only}]({path})\n")

        path = os.path.join(self.output_dir, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        logger.info(f"Markdown report saved to {path}")
        return path

    # ------------------------------------------------------------------
    # PDF export
    # ------------------------------------------------------------------
    def save_pdf(self, filename: str = "eda_report.pdf") -> str:
        path = os.path.join(self.output_dir, filename)
        doc = SimpleDocTemplate(
            path, pagesize=A4,
            topMargin=2 * cm, bottomMargin=2 * cm, leftMargin=2 * cm, rightMargin=2 * cm,
        )
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle("ReportTitle", parent=styles["Title"], fontSize=20, spaceAfter=6)
        heading_style = ParagraphStyle("ReportHeading", parent=styles["Heading2"],
                                        spaceBefore=14, spaceAfter=8, textColor=colors.HexColor("#1B4965"))
        body_style = ParagraphStyle("ReportBody", parent=styles["BodyText"], spaceAfter=6, leading=14)

        story = []
        for section in self.sections:
            if section["type"] == "title":
                story.append(Paragraph(section["heading"], title_style))
                story.append(Paragraph(f"Generated on {section['content']}", body_style))
                story.append(Spacer(1, 12))
            elif section["type"] == "text":
                story.append(Paragraph(section["heading"], heading_style))
                for line in str(section["content"]).split("\n"):
                    clean = line.replace("**", "").replace("`", "")
                    if clean.strip():
                        story.append(Paragraph(clean, body_style))
            elif section["type"] == "table":
                story.append(Paragraph(section["heading"], heading_style))
                story.append(self._df_to_pdf_table(section["content"]))
                story.append(Spacer(1, 10))
            elif section["type"] == "images":
                story.append(Paragraph(section["heading"], heading_style))
                for img_path in section["content"]:
                    if os.path.exists(img_path):
                        story.append(PageBreak())
                        story.append(Image(img_path, width=16 * cm, height=10 * cm, kind="proportional"))

        doc.build(story)
        logger.info(f"PDF report saved to {path}")
        return path

    @staticmethod
    def _df_to_pdf_table(df: pd.DataFrame, max_rows: int = 25, page_width_cm: float = 17.0) -> Table:
        display_df = df.reset_index() if df.index.name or not isinstance(df.index, pd.RangeIndex) else df
        display_df = display_df.head(max_rows)

        styles = getSampleStyleSheet()
        cell_style = ParagraphStyle("cell", parent=styles["BodyText"], fontSize=7, leading=8.5)
        header_style = ParagraphStyle("header", parent=styles["BodyText"], fontSize=7.5,
                                       leading=9, textColor=colors.white)

        # Wrap every cell in a Paragraph so long content wraps instead of
        # overflowing the page, and distribute the fixed page width evenly
        # across however many columns this particular table has.
        header_row = [Paragraph(str(c), header_style) for c in display_df.columns]
        data = [header_row]
        for _, row in display_df.iterrows():
            cells = [Paragraph("" if pd.isna(val) else str(val), cell_style) for val in row.tolist()]
            data.append(cells)

        n_cols = len(display_df.columns)
        col_width = (page_width_cm * cm) / max(n_cols, 1)
        table = Table(data, repeatRows=1, colWidths=[col_width] * n_cols)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1B4965")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F0F4F8")]),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 3),
            ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ]))
        return table

    # ------------------------------------------------------------------
    # Excel export
    # ------------------------------------------------------------------
    def save_excel(self, filename: str = "eda_report.xlsx") -> str:
        path = os.path.join(self.output_dir, filename)
        with pd.ExcelWriter(path, engine="openpyxl") as writer:
            summary_rows = [{"Section": s["heading"], "Type": s["type"]} for s in self.sections]
            pd.DataFrame(summary_rows).to_excel(writer, sheet_name="Summary", index=False)

            used_names = set()
            for section in self.sections:
                if section["type"] != "table":
                    continue
                sheet_name = self._safe_sheet_name(section["heading"], used_names)
                df = section["content"]
                df_to_write = df.reset_index() if df.index.name else df
                df_to_write.to_excel(writer, sheet_name=sheet_name, index=False)
        logger.info(f"Excel report saved to {path}")
        return path

    @staticmethod
    def _safe_sheet_name(heading: str, used_names: set) -> str:
        name = "".join(c for c in heading if c not in r'[]:*?/\\')[:31] or "Sheet"
        base, i = name, 1
        while name in used_names:
            suffix = f"_{i}"
            name = base[: 31 - len(suffix)] + suffix
            i += 1
        used_names.add(name)
        return name

    # ------------------------------------------------------------------
    # CSV summary export
    # ------------------------------------------------------------------
    def save_csv_summary(self, filename: str = "eda_summary.csv") -> str:
        """Export every table-type section as one combined long-format CSV."""
        path = os.path.join(self.output_dir, filename)
        rows = []
        for section in self.sections:
            if section["type"] != "table":
                continue
            df = section["content"]
            for _, row in df.reset_index(drop=True).iterrows():
                row_dict = row.to_dict()
                row_dict["_section"] = section["heading"]
                rows.append(row_dict)
        combined = pd.DataFrame(rows)
        combined.to_csv(path, index=False)
        logger.info(f"CSV summary saved to {path}")
        return path

    # ------------------------------------------------------------------
    # Convenience: export everything at once
    # ------------------------------------------------------------------
    def save_all(self, base_filename: str = "eda_report") -> dict:
        return {
            "markdown": self.save_markdown(f"{base_filename}.md"),
            "pdf": self.save_pdf(f"{base_filename}.pdf"),
            "excel": self.save_excel(f"{base_filename}.xlsx"),
            "csv": self.save_csv_summary(f"{base_filename}_summary.csv"),
        }
