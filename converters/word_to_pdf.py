import os
import subprocess

def convert_word_to_pdf(input_docx: str, output_dir: str) -> str:
    try:
        cmd = [
            "soffice",
            "--headless",
            "--convert-to", "pdf",
            "--outdir", output_dir,
            input_docx
        ]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60)
        if res.returncode != 0:
            raise RuntimeError(f"LibreOffice error: {res.stderr.decode('utf-8')}")

        base_name = os.path.splitext(os.path.basename(input_docx))[0]
        output_pdf = os.path.join(output_dir, f"{base_name}.pdf")

        if os.path.exists(output_pdf):
            return output_pdf
        raise FileNotFoundError("LibreOffice failed to generate the PDF file.")
    except Exception as e:
        raise RuntimeError(f"Word to PDF conversion failed: {e}")
