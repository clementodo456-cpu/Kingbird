import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def convert_text_to_pdf(text_str: str, output_pdf: str) -> bool:
    try:
        doc = SimpleDocTemplate(output_pdf, pagesize=letter)
        styles = getSampleStyleSheet()
        normal_style = styles['Normal']
        normal_style.fontSize = 11
        normal_style.leading = 14

        story = []
        lines = text_str.split("\n")
        for line in lines:
            safe_line = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            if safe_line.strip() == "":
                story.append(Spacer(1, 10))
            else:
                story.append(Paragraph(safe_line, normal_style))

        doc.build(story)
        return os.path.exists(output_pdf)
    except Exception as e:
        raise RuntimeError(f"Text to PDF conversion failed: {e}")
