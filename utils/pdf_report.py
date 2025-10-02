from typing import List, Dict
import os
import io
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, PageBreak


def save_session_report(
    pdf_path: str,
    session_records: List[Dict],
    model_name: str,
    capture_interval: float,
    total_duration: float,
):
    # Ensure the directory exists if path contains a directory
    pdf_dir = os.path.dirname(pdf_path)
    if pdf_dir:  # Only create directory if there's actually a directory in the path
        os.makedirs(pdf_dir, exist_ok=True)
    
    doc = SimpleDocTemplate(pdf_path, pagesize=A4)
    styles = getSampleStyleSheet()
    elems = []

    title = f"Reporte de sesión - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    elems.append(Paragraph(title, styles['Title']))
    elems.append(Spacer(1, 12))

    meta = [
        ["Modelo", model_name or "-"] ,
        ["Intervalo de captura (s)", f"{capture_interval:.2f}"],
        ["Duración total (s)", f"{total_duration:.1f}"],
        ["Detecciones", str(len(session_records))],
    ]
    t = Table(meta, hAlign='LEFT', colWidths=[170, 350])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('BACKGROUND', (0,1), (-1,-1), colors.beige),
    ]))
    elems.append(t)
    elems.append(Spacer(1, 16))

    if not session_records:
        elems.append(Paragraph("No hubo detecciones durante la sesión.", styles['Normal']))
    else:
        for i, rec in enumerate(session_records, start=1):
            elems.append(Paragraph(f"Detección #{i}", styles['Heading2']))
            details = [
                ["Hora", rec.get('timestamp', '-')],
                ["Emoción", rec.get('emotion', '-')],
                ["Confianza", f"{rec.get('confidence', 0.0)*100:.1f}%"],
                ["Modelo", rec.get('model', '-')],
            ]
            tb = Table(details, hAlign='LEFT', colWidths=[170, 350])
            tb.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ]))
            elems.append(tb)
            elems.append(Spacer(1, 8))

            # Handle image data stored in memory
            img_data = rec.get('img_data')
            if img_data:
                # Fit image into width
                max_w = 450
                max_h = 300
                try:
                    img_stream = io.BytesIO(img_data)
                    im = RLImage(img_stream)
                    iw, ih = im.wrap(0, 0)
                    scale = min(max_w/iw, max_h/ih)
                    im.drawWidth = iw * scale
                    im.drawHeight = ih * scale
                    elems.append(im)
                except Exception:
                    # ignore image failures; continue
                    pass
                elems.append(Spacer(1, 12))

            if i < len(session_records):
                elems.append(PageBreak())

    doc.build(elems)
