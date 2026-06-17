import io
import re

from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)


def _markdown_to_paragraphs(markdown: str, styles) -> list:
    """Convert markdown text to ReportLab paragraphs."""
    elements = []
    lines = markdown.split("\n")

    for line in lines:
        line = line.strip()
        if not line:
            elements.append(Spacer(1, 6))
            continue

        # H1
        if line.startswith("# "):
            text = line[2:].strip()
            elements.append(Paragraph(text, styles["H1"]))
            elements.append(Spacer(1, 12))

        # H2
        elif line.startswith("## "):
            text = line[3:].strip()
            elements.append(Paragraph(text, styles["H2"]))
            elements.append(Spacer(1, 8))

        # H3
        elif line.startswith("### "):
            text = line[4:].strip()
            elements.append(Paragraph(text, styles["H3"]))
            elements.append(Spacer(1, 6))

        # Bullet list
        elif line.startswith("- ") or line.startswith("* "):
            text = line[2:].strip()
            text = _format_inline(text)
            elements.append(Paragraph(f"• {text}", styles["Bullet"]))

        # Numbered list
        elif re.match(r"^\d+\.\s", line):
            text = re.sub(r"^\d+\.\s", "", line)
            text = _format_inline(text)
            elements.append(Paragraph(text, styles["Bullet"]))

        # Normal paragraph
        else:
            text = _format_inline(line)
            elements.append(Paragraph(text, styles["Body"]))
            elements.append(Spacer(1, 4))

    return elements


def _format_inline(text: str) -> str:
    """Convert basic markdown (bold, italic, code) to ReportLab markup."""
    # Bold: **text** → <b>text</b>
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    # Italic: *text* → <i>text</i>
    text = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<i>\1</i>", text)
    # Inline code: `text` → <font face="Courier">text</font>
    text = re.sub(r"`(.+?)`", r'<font face="Courier" color="#d63384">\1</font>', text)
    return text


def _build_styles():
    """Build custom paragraph styles."""
    base = getSampleStyleSheet()

    styles = {
        "H1": ParagraphStyle(
            "H1",
            parent=base["Heading1"],
            fontSize=24,
            textColor=HexColor("#1a1a1a"),
            spaceAfter=12,
            fontName="Helvetica-Bold",
        ),
        "H2": ParagraphStyle(
            "H2",
            parent=base["Heading2"],
            fontSize=18,
            textColor=HexColor("#2563eb"),
            spaceAfter=10,
            fontName="Helvetica-Bold",
        ),
        "H3": ParagraphStyle(
            "H3",
            parent=base["Heading3"],
            fontSize=14,
            textColor=HexColor("#1e40af"),
            spaceAfter=8,
            fontName="Helvetica-Bold",
        ),
        "Body": ParagraphStyle(
            "Body",
            parent=base["BodyText"],
            fontSize=11,
            leading=16,
            textColor=HexColor("#1a1a1a"),
            alignment=TA_LEFT,
        ),
        "Bullet": ParagraphStyle(
            "Bullet",
            parent=base["BodyText"],
            fontSize=11,
            leading=16,
            leftIndent=20,
            textColor=HexColor("#1a1a1a"),
        ),
    }
    return styles


def generate_pdf(title: str, content: str) -> bytes:
    """
    Generate a styled PDF from markdown content.

    Args:
        title: Video title (used as document header)
        content: Markdown-formatted notes from LLM

    Returns:
        PDF as bytes
    """
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=0.7 * inch,
        leftMargin=0.7 * inch,
        topMargin=0.7 * inch,
        bottomMargin=0.7 * inch,
        title=title,
    )

    styles = _build_styles()
    elements = []

    # Title page header
    elements.append(Paragraph(title, styles["H1"]))
    elements.append(Spacer(1, 20))

    # Markdown content
    elements.extend(_markdown_to_paragraphs(content, styles))

    doc.build(elements)
    pdf_bytes = buffer.getvalue()
    buffer.close()

    return pdf_bytes