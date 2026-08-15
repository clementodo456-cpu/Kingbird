import os
from pdf2docx import Converter

def convert_pdf_to_word(input_pdf: str, output_docx: str) -> bool:
    cv = None
    try:
        cv = Converter(input_pdf)
        cv.convert(output_docx, start=0, end=None)
        return os.path.exists(output_docx) and os.path.getsize(output_docx) > 0
    except Exception as e:
        raise RuntimeError(f"PDF to Word conversion failed: {e}")
    finally:
        if cv:
            cv.close()
