import os
import fitz  # PyMuPDF

def convert_pdf_to_text(input_pdf: str, output_txt: str) -> bool:
    try:
        doc = fitz.open(input_pdf)
        if doc.is_encrypted:
            raise ValueError("Password-protected PDF files are not supported.")

        text_content = []
        for page in doc:
            text_content.append(page.get_text())

        full_text = "\n--- Page Break ---\n".join(text_content).strip()
        if not full_text:
            full_text = "No extractable text found in this PDF document."

        with open(output_txt, "w", encoding="utf-8") as f:
            f.write(full_text)

        return os.path.exists(output_txt)
    except Exception as e:
        raise RuntimeError(f"PDF to Text conversion failed: {e}")
