from __future__ import annotations

import html
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
)


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "docs" / "collaboration"
OUTPUT_DIR = ROOT / "docs" / "pdf"

DOCUMENTS = {
    "contracts-and-change-impact.md": "AIlegato-contracts-and-change-impact.pdf",
    "person-a-go-backend-plan.md": "AIlegato-person-a-go-traffic-backend-plan.pdf",
    "person-b-go-core-backend-plan.md": "AIlegato-person-b-go-core-backend-plan.pdf",
    "person-c-python-ml-plan.md": "AIlegato-person-c-python-ml-plan.pdf",
}


def register_fonts() -> tuple[str, str]:
    regular = Path("C:/Windows/Fonts/arial.ttf")
    bold = Path("C:/Windows/Fonts/arialbd.ttf")
    if regular.exists() and bold.exists():
        pdfmetrics.registerFont(TTFont("DocFont", str(regular)))
        pdfmetrics.registerFont(TTFont("DocFont-Bold", str(bold)))
        return "DocFont", "DocFont-Bold"
    return "Helvetica", "Helvetica-Bold"


def build_styles(font_name: str, bold_font_name: str) -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "DocTitle",
            parent=base["Title"],
            fontName=bold_font_name,
            fontSize=22,
            leading=28,
            alignment=TA_CENTER,
            spaceAfter=12,
        ),
        "h1": ParagraphStyle(
            "H1",
            parent=base["Heading1"],
            fontName=bold_font_name,
            fontSize=17,
            leading=22,
            spaceBefore=10,
            spaceAfter=8,
        ),
        "h2": ParagraphStyle(
            "H2",
            parent=base["Heading2"],
            fontName=bold_font_name,
            fontSize=13,
            leading=17,
            spaceBefore=8,
            spaceAfter=6,
        ),
        "body": ParagraphStyle(
            "Body",
            parent=base["BodyText"],
            fontName=font_name,
            fontSize=10,
            leading=14,
            spaceAfter=5,
        ),
        "bullet": ParagraphStyle(
            "Bullet",
            parent=base["BodyText"],
            fontName=font_name,
            fontSize=10,
            leading=14,
            leftIndent=8 * mm,
            firstLineIndent=-4 * mm,
            spaceAfter=3,
        ),
        "code": ParagraphStyle(
            "Code",
            parent=base["Code"],
            fontName="Courier",
            fontSize=7.5,
            leading=10,
            backColor=colors.HexColor("#F3F4F6"),
            borderColor=colors.HexColor("#D1D5DB"),
            borderWidth=0.25,
            borderPadding=5,
            spaceBefore=4,
            spaceAfter=8,
        ),
    }


def clean_inline(text: str) -> str:
    escaped = html.escape(text)
    return escaped.replace("`", "")


def markdown_to_flowables(markdown: str, styles: dict[str, ParagraphStyle]) -> list:
    flowables = []
    in_code = False
    code_lines: list[str] = []

    for raw_line in markdown.splitlines():
        line = raw_line.rstrip()
        if line.startswith("```"):
            if in_code:
                flowables.append(Preformatted("\n".join(code_lines), styles["code"]))
                code_lines = []
                in_code = False
            else:
                in_code = True
            continue

        if in_code:
            code_lines.append(line)
            continue

        if not line:
            flowables.append(Spacer(1, 3))
            continue

        if line.startswith("# "):
            if flowables:
                flowables.append(PageBreak())
            flowables.append(Paragraph(clean_inline(line[2:]), styles["title"]))
            flowables.append(Spacer(1, 8))
            continue

        if line.startswith("## "):
            flowables.append(Paragraph(clean_inline(line[3:]), styles["h1"]))
            continue

        if line.startswith("### "):
            flowables.append(Paragraph(clean_inline(line[4:]), styles["h2"]))
            continue

        if line.startswith("- "):
            flowables.append(Paragraph(f"- {clean_inline(line[2:])}", styles["bullet"]))
            continue

        if len(line) > 3 and line[0].isdigit() and ". " in line[:5]:
            flowables.append(Paragraph(clean_inline(line), styles["bullet"]))
            continue

        flowables.append(Paragraph(clean_inline(line), styles["body"]))

    if code_lines:
        flowables.append(Preformatted("\n".join(code_lines), styles["code"]))

    return flowables


def page_footer(canvas, doc) -> None:
    canvas.saveState()
    canvas.setFont("DocFont" if "DocFont" in pdfmetrics.getRegisteredFontNames() else "Helvetica", 8)
    canvas.setFillColor(colors.grey)
    canvas.drawString(18 * mm, 10 * mm, "AIlegato")
    canvas.drawRightString(A4[0] - 18 * mm, 10 * mm, f"Страница {doc.page}")
    canvas.restoreState()


def build_pdf(source: Path, target: Path, styles: dict[str, ParagraphStyle]) -> None:
    doc = SimpleDocTemplate(
        str(target),
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        title=target.stem,
    )
    content = source.read_text(encoding="utf-8")
    flowables = markdown_to_flowables(content, styles)
    doc.build(flowables, onFirstPage=page_footer, onLaterPages=page_footer)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    font_name, bold_font_name = register_fonts()
    styles = build_styles(font_name, bold_font_name)

    for source_name, output_name in DOCUMENTS.items():
        build_pdf(SOURCE_DIR / source_name, OUTPUT_DIR / output_name, styles)
        print(f"generated {OUTPUT_DIR / output_name}")


if __name__ == "__main__":
    main()
