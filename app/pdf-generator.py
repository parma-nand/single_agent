from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors

def generate_resume_report(score: int, strengths: list, improvements: list, output_path="resume_report.pdf"):
    pdf = SimpleDocTemplate(output_path, rightMargin=inch, leftMargin=inch,
                            topMargin=inch, bottomMargin=inch)
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle("Title", parent=styles["Heading1"], fontSize=18, spaceAfter=6)
    score_style = ParagraphStyle("Score", parent=styles["Normal"], fontSize=14, textColor=colors.darkgreen)
    section_style = ParagraphStyle("Section", parent=styles["Heading2"], fontSize=12, spaceBefore=12)
    body_style = styles["BodyText"]

    elements = []

    elements.append(Paragraph("Resume Analysis Report", title_style))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.grey))
    elements.append(Spacer(1, 0.2 * inch))

    elements.append(Paragraph(f"Resume Score: {score}/100", score_style))
    elements.append(Spacer(1, 0.2 * inch))

    elements.append(Paragraph("Strengths", section_style))
    for s in strengths:
        elements.append(Paragraph(f"• {s}", body_style))

    elements.append(Spacer(1, 0.1 * inch))
    elements.append(Paragraph("Areas for Improvement", section_style))
    for imp in improvements:
        elements.append(Paragraph(f"• {imp}", body_style))

    pdf.build(elements)
    print(f"Report saved to {output_path}")

# Usage
generate_resume_report(
    score=85,
    strengths=["Strong Java skills", "Spring Boot experience"],
    improvements=["Add more quantified achievements"]
)