"""
pdf_generator.py
----------------
Generates a Resume Analysis Report PDF from structured LLM output.

In your LangGraph/single-agent pipeline, call:
    generate_resume_report(llm_output_dict, output_path="resume_report.pdf")

LLM output dict shape (parse your LLM's text into this):
{
    "candidate_name": str,
    "score": int,                      # 0–100
    "summary": str,                    # 2–3 sentence overview
    "strengths": list[str],
    "improvements": list[str],
    "missing_keywords": list[str],
    "ats_tips": list[str],
    "recommended_roles": list[str],
}
"""

from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime


# ─────────────────────────────────────────────
#  COLOUR PALETTE
# ─────────────────────────────────────────────
DARK_BLUE   = colors.HexColor("#1A237E")
MID_BLUE    = colors.HexColor("#283593")
ACCENT_BLUE = colors.HexColor("#3949AB")
LIGHT_BG    = colors.HexColor("#E8EAF6")
GREEN       = colors.HexColor("#2E7D32")
AMBER       = colors.HexColor("#F57F17")
RED         = colors.HexColor("#B71C1C")
GREY_TEXT   = colors.HexColor("#424242")
LIGHT_GREY  = colors.HexColor("#F5F5F5")
WHITE       = colors.white


def _score_color(score: int):
    if score >= 75:
        return GREEN
    elif score >= 50:
        return AMBER
    return RED


def _build_styles():
    base = getSampleStyleSheet()

    styles = {
        "header_name": ParagraphStyle(
            "HeaderName",
            parent=base["Normal"],
            fontSize=22,
            textColor=WHITE,
            fontName="Helvetica-Bold",
            alignment=TA_CENTER,
            spaceAfter=2,
        ),
        "header_sub": ParagraphStyle(
            "HeaderSub",
            parent=base["Normal"],
            fontSize=10,
            textColor=colors.HexColor("#C5CAE9"),
            fontName="Helvetica",
            alignment=TA_CENTER,
            spaceAfter=0,
        ),
        "section_title": ParagraphStyle(
            "SectionTitle",
            parent=base["Normal"],
            fontSize=12,
            textColor=DARK_BLUE,
            fontName="Helvetica-Bold",
            spaceBefore=14,
            spaceAfter=4,
        ),
        "body": ParagraphStyle(
            "Body",
            parent=base["Normal"],
            fontSize=10,
            textColor=GREY_TEXT,
            fontName="Helvetica",
            leading=15,
            spaceAfter=3,
        ),
        "bullet": ParagraphStyle(
            "Bullet",
            parent=base["Normal"],
            fontSize=10,
            textColor=GREY_TEXT,
            fontName="Helvetica",
            leading=14,
            leftIndent=12,
            spaceAfter=3,
        ),
        "score_label": ParagraphStyle(
            "ScoreLabel",
            parent=base["Normal"],
            fontSize=11,
            textColor=GREY_TEXT,
            fontName="Helvetica",
            alignment=TA_CENTER,
        ),
        "score_number": ParagraphStyle(
            "ScoreNumber",
            parent=base["Normal"],
            fontSize=36,
            fontName="Helvetica-Bold",
            alignment=TA_CENTER,
        ),
        "footer": ParagraphStyle(
            "Footer",
            parent=base["Normal"],
            fontSize=8,
            textColor=colors.HexColor("#9E9E9E"),
            alignment=TA_CENTER,
        ),
    }
    return styles


def _header_table(candidate_name: str, styles: dict):
    """Dark blue banner with candidate name."""
    name_para = Paragraph(candidate_name, styles["header_name"])
    sub_para  = Paragraph("Resume Analysis Report", styles["header_sub"])

    tbl = Table([[name_para], [sub_para]], colWidths=[6.3 * inch])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",  (0, 0), (-1, -1), DARK_BLUE),
        ("TOPPADDING",  (0, 0), (-1, -1), 18),
        ("BOTTOMPADDING", (0, -1), (-1, -1), 18),
        ("LEFTPADDING",  (0, 0), (-1, -1), 20),
        ("RIGHTPADDING", (0, 0), (-1, -1), 20),
        ("ROUNDEDCORNERS", [6]),
    ]))
    return tbl


def _score_table(score: int, styles: dict):
    """Compact score card: big number on left, colour-coded bar on right."""
    score_num = Paragraph(
        f'<font color="{_score_color(score).hexval()}"><b>{score}</b></font>',
        styles["score_number"],
    )
    score_lbl = Paragraph("out of 100", styles["score_label"])

    # Simple band label
    if score >= 75:
        band, band_color = "Strong Match", GREEN
    elif score >= 50:
        band, band_color = "Moderate Match", AMBER
    else:
        band, band_color = "Needs Work", RED

    band_para = Paragraph(
        f'<font color="{band_color.hexval()}"><b>{band}</b></font>',
        styles["score_label"],
    )

    inner = Table(
        [[score_num, score_lbl, band_para]],
        colWidths=[1.2 * inch, 1.2 * inch, 3.9 * inch],
    )
    inner.setStyle(TableStyle([
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING",    (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ]))

    outer = Table([[inner]], colWidths=[6.3 * inch])
    outer.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), LIGHT_BG),
        ("TOPPADDING",    (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ("LEFTPADDING",   (0, 0), (-1, -1), 0),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 0),
        ("BOX",           (0, 0), (-1, -1), 1, colors.HexColor("#C5CAE9")),
    ]))
    return outer


def _two_col_lists(left_title, left_items, right_title, right_items, styles):
    """Side-by-side bulleted lists (strengths vs improvements)."""
    def make_cell(title, items, bg):
        cell = [Paragraph(title, styles["section_title"])]
        cell.append(HRFlowable(width="100%", thickness=1, color=ACCENT_BLUE, spaceAfter=4))
        for item in items:
            cell.append(Paragraph(f"• {item}", styles["bullet"]))
        return cell

    left_cell  = make_cell(left_title,  left_items,  LIGHT_BG)
    right_cell = make_cell(right_title, right_items, colors.HexColor("#FFF8E1"))

    tbl = Table(
        [[left_cell, right_cell]],
        colWidths=[3.1 * inch, 3.1 * inch],
        hAlign="LEFT",
    )
    tbl.setStyle(TableStyle([
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
        ("BACKGROUND",    (0, 0), (0, 0),   LIGHT_BG),
        ("BACKGROUND",    (1, 0), (1, 0),   colors.HexColor("#FFF8E1")),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("BOX",           (0, 0), (0, 0),   1, colors.HexColor("#C5CAE9")),
        ("BOX",           (1, 0), (1, 0),   1, colors.HexColor("#FFE082")),
        ("COLUMNPADDING", (0, 0), (-1, -1), 6),
    ]))
    return tbl


def _tag_row(items: list, styles: dict):
    """Renders items as small pill-style tags in a wrapping paragraph."""
    if not items:
        return Paragraph("None identified.", styles["body"])
    tags_html = "  ".join(
        f'<font backColor="{LIGHT_BG.hexval()}"> {item} </font>'
        for item in items
    )
    return Paragraph(tags_html, styles["body"])


def generate_resume_report(llm_output: dict, output_path: str = "resume_report.pdf"):
    """
    Main entry point. Pass in your parsed LLM output dict and an output path.
    """
    styles = _build_styles()

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=0.85 * inch,
        leftMargin=0.85 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    )

    story = []

    # ── HEADER ──────────────────────────────────────────────────────
    story.append(_header_table(llm_output.get("candidate_name", "Candidate"), styles))
    story.append(Spacer(1, 0.18 * inch))

    # ── SCORE CARD ──────────────────────────────────────────────────
    story.append(_score_table(llm_output.get("score", 0), styles))
    story.append(Spacer(1, 0.18 * inch))

    # ── SUMMARY ─────────────────────────────────────────────────────
    story.append(Paragraph("Overview", styles["section_title"]))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT_BLUE, spaceAfter=6))
    story.append(Paragraph(llm_output.get("summary", ""), styles["body"]))
    story.append(Spacer(1, 0.1 * inch))

    # ── STRENGTHS vs IMPROVEMENTS (two-column) ──────────────────────
    story.append(
        _two_col_lists(
            "✓  Strengths",        llm_output.get("strengths", []),
            "⚠  Areas to Improve", llm_output.get("improvements", []),
            styles,
        )
    )
    story.append(Spacer(1, 0.15 * inch))

    # ── MISSING KEYWORDS ────────────────────────────────────────────
    story.append(Paragraph("Missing Keywords / Skills", styles["section_title"]))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT_BLUE, spaceAfter=6))
    for kw in llm_output.get("missing_keywords", []):
        story.append(Paragraph(f"• {kw}", styles["bullet"]))
    story.append(Spacer(1, 0.1 * inch))

    # ── ATS TIPS ────────────────────────────────────────────────────
    story.append(Paragraph("ATS Optimisation Tips", styles["section_title"]))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT_BLUE, spaceAfter=6))
    for tip in llm_output.get("ats_tips", []):
        story.append(Paragraph(f"• {tip}", styles["bullet"]))
    story.append(Spacer(1, 0.1 * inch))

    # ── RECOMMENDED ROLES ───────────────────────────────────────────
    story.append(Paragraph("Recommended Job Roles", styles["section_title"]))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT_BLUE, spaceAfter=6))
    roles = llm_output.get("recommended_roles", [])
    if roles:
        roles_text = "  |  ".join(roles)
        story.append(Paragraph(roles_text, styles["body"]))
    story.append(Spacer(1, 0.2 * inch))

    # ── FOOTER ──────────────────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#BDBDBD")))
    story.append(Spacer(1, 0.06 * inch))
    generated_on = datetime.now().strftime("%d %b %Y, %I:%M %p")
    story.append(Paragraph(
        f"Generated by Resume Intelligence Platform  •  {generated_on}",
        styles["footer"],
    ))

    doc.build(story)
    print(f"[✓] Report saved → {output_path}")
    return output_path


# ─────────────────────────────────────────────────────────────────────────────
#  DEMO  —  simulates what your LLM node would return after analysing the CV
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":

    # This dict would come from your LLM output parser in LangGraph
    sample_llm_output = {
        "candidate_name": "Parma Nand Thakur",
        "score": 72,
        "summary": (
            "Parma is a backend-leaning full-stack developer with 3+ years at Capgemini "
            "in capital markets. His resume demonstrates strong Java/Spring Boot ownership "
            "and measurable impact (70% manual effort reduction, 30% load time improvement). "
            "To break into AI/ML engineering roles, he should surface his GenAI and LLM work "
            "more prominently and add depth to ML fundamentals."
        ),
        "strengths": [
            "Quantified achievements (70% effort reduction, 50% productivity gain)",
            "Capital markets domain experience — valued in fintech AI roles",
            "Full-stack breadth: Java, Spring Boot, React.js, PostgreSQL",
            "CI/CD, Microservices, and AWS fundamentals in skills section",
            "Clean project descriptions with clear tech stack attribution",
        ],
        "improvements": [
            "GenAI/LLM work at Capgemini is completely absent — add it",
            "Executive summary still says 'Java Full Stack Developer'; update to AI/ML Engineer",
            "No mention of RAG pipelines, LangChain, Qdrant, or fine-tuning work",
            "Projects section has no AI/ML projects — add Resume Intelligence Platform",
            "Skills section missing: Python, LangChain, HuggingFace, FastAPI, Docker",
        ],
        "missing_keywords": [
            "Python", "LangChain", "RAG", "LLM fine-tuning", "FastAPI",
            "Docker", "HuggingFace", "Vector Database", "Qdrant", "NLP",
            "Prompt Engineering", "Transformers", "FAISS / ChromaDB",
        ],
        "ats_tips": [
            "Replace 'Senior Software Engineer' title with 'AI/ML Engineer' or 'GenAI Engineer'",
            "Add a dedicated 'AI / ML' skills sub-section above Java skills",
            "Use keywords from JD verbatim: 'retrieval-augmented generation', 'embedding models'",
            "Move education after experience (you have 3+ years XP, lead with impact)",
            "Add GitHub links to your AI portfolio projects (ai-engineer-journey repo)",
        ],
        "recommended_roles": [
            "GenAI Engineer", "AI/ML Engineer", "Applied AI Engineer",
            "LLM Engineer", "Backend Engineer (AI Products)"
        ],
    }

    generate_resume_report(sample_llm_output, "resume_report.pdf")