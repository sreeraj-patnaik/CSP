"""PDF report generation using ReportLab."""
import io
from datetime import date
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from apps.surveys.models import SurveyResponse
from apps.villages.models import Village
from apps.analytics import insights as ins


BRAND_DARK  = colors.HexColor("#0F172A")
BRAND_CYAN  = colors.HexColor("#06B6D4")
BRAND_LIGHT = colors.HexColor("#F8FAFC")
BRAND_MUTED = colors.HexColor("#94A3B8")


def _styles():
    ss = getSampleStyleSheet()
    ss.add(ParagraphStyle("Title2", parent=ss["Title"],
           textColor=BRAND_DARK, fontSize=24, spaceAfter=6))
    ss.add(ParagraphStyle("SubTitle", parent=ss["Normal"],
           textColor=BRAND_CYAN, fontSize=13, spaceAfter=12))
    ss.add(ParagraphStyle("Body2", parent=ss["Normal"],
           textColor=BRAND_DARK, fontSize=10, spaceAfter=6))
    ss.add(ParagraphStyle("Muted", parent=ss["Normal"],
           textColor=BRAND_MUTED, fontSize=9))
    ss.add(ParagraphStyle("SectionHead", parent=ss["Heading2"],
           textColor=BRAND_CYAN, fontSize=14, spaceBefore=16, spaceAfter=6))
    return ss


def generate_summary_pdf():
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm,
        title="CSP Survey Summary Report",
    )
    ss = _styles()
    story = []

    # Header
    story.append(Paragraph("Community Service Project", ss["Title2"]))
    story.append(Paragraph("Safe Usage of Internet &amp; Cybercrime Awareness in Rural Areas", ss["SubTitle"]))
    story.append(Paragraph(f"Survey Summary Report — Generated {date.today().strftime('%B %d, %Y')}", ss["Muted"]))
    story.append(HRFlowable(width="100%", thickness=2, color=BRAND_CYAN, spaceAfter=12))

    total = SurveyResponse.objects.count()
    internet_users = SurveyResponse.objects.filter(uses_internet=True).count()
    internet_pct = round((internet_users / total * 100) if total else 0, 1)

    story.append(Paragraph("Overview", ss["SectionHead"]))
    summary_data = [
        ["Metric", "Value"],
        ["Total Survey Responses", str(total)],
        ["Internet Users", f"{internet_users} ({internet_pct}%)"],
        ["Villages Covered", str(Village.objects.filter(is_active=True).count())],
        ["Report Date", date.today().strftime("%Y-%m-%d")],
    ]
    tbl = Table(summary_data, colWidths=[9*cm, 6*cm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), BRAND_DARK),
        ("TEXTCOLOR", (0, 0), (-1, 0), BRAND_LIGHT),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F1F5F9")]),
        ("GRID", (0, 0), (-1, -1), 0.5, BRAND_MUTED),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 12))

    # Village breakdown
    story.append(Paragraph("Village-wise Statistics", ss["SectionHead"]))
    vc = ins.village_comparison()
    if vc:
        vdata = [["Village", "Responses", "Internet Users", "Internet %", "Avg Awareness"]]
        for row in vc:
            vdata.append([
                row.get("village", ""),
                str(row.get("total", 0)),
                str(row.get("internet_users", 0)),
                f"{row.get('internet_pct', 0)}%",
                str(row.get("avg_awareness", 0)),
            ])
        vtbl = Table(vdata, colWidths=[4*cm, 3*cm, 3.5*cm, 3*cm, 3.5*cm])
        vtbl.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), BRAND_DARK),
            ("TEXTCOLOR", (0, 0), (-1, 0), BRAND_LIGHT),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F1F5F9")]),
            ("GRID", (0, 0), (-1, -1), 0.5, BRAND_MUTED),
            ("ALIGN", (1, 0), (-1, -1), "CENTER"),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(vtbl)

    story.append(Spacer(1, 12))

    # Auto insights
    story.append(Paragraph("Key Findings", ss["SectionHead"]))
    auto_insights = ins.generate_auto_insights()
    for insight in auto_insights:
        story.append(Paragraph(
            f"<b>{insight['title']}:</b> {insight['text']}",
            ss["Body2"]
        ))
        story.append(Spacer(1, 4))

    doc.build(story)
    buffer.seek(0)
    return buffer
