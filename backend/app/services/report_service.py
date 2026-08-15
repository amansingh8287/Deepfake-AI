import json
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.config import get_settings
from app.models import Detection
from app.schemas import SuspiciousFrame
from app.services.file_service import safe_report_filename

DISCLAIMER = (
    "DeepGuard AI provides an AI-based prediction and should not be treated as definitive proof "
    "that media is authentic or manipulated."
)


def build_report(detection: Detection) -> Path:
    settings = get_settings()
    report_name = safe_report_filename(detection.filename, detection.id)
    report_path = settings.report_dir / report_name

    doc = SimpleDocTemplate(str(report_path), pagesize=A4, topMargin=20 * mm, bottomMargin=20 * mm)
    styles = getSampleStyleSheet()
    title = ParagraphStyle("Title", parent=styles["Heading1"], textColor=colors.HexColor("#00d4ff"))
    body = styles["BodyText"]
    story = [
        Paragraph("DeepGuard AI Detection Report", title),
        Spacer(1, 8),
        Paragraph("Final-year project report artifact for local detection analysis.", body),
        Spacer(1, 12),
    ]

    suspicious = json.loads(detection.suspicious_frames or "[]")
    suspicious_lines = "<br/>".join(
        f"Frame {item['index']} at {item['timestamp']:.2f}s ({item['confidence']:.1f}% confidence) - {item['note']}"
        for item in suspicious
    ) or "No suspicious frames highlighted."

    rows = [
        ["Field", "Value"],
        ["File name", detection.filename],
        ["Media type", detection.media_type],
        ["Prediction", detection.prediction],
        ["Confidence", f"{detection.confidence:.2f}%"],
        ["Processing time", f"{detection.processing_time:.2f} seconds"],
        ["Faces detected", str(detection.faces_detected)],
        ["Frames analyzed", str(detection.frames_analyzed)],
        ["Model", detection.model_name],
        ["Mode", detection.mode],
        ["Suspicious frames", suspicious_lines],
        ["Explanation", detection.explanation],
        ["Disclaimer", DISCLAIMER],
    ]

    table = Table(rows, colWidths=[45 * mm, 130 * mm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#111827")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("PADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.append(table)
    doc.build(story)
    return report_path

