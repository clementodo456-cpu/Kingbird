import os
import zipfile
from pdf2image import convert_from_path

def convert_pdf_to_images(input_pdf: str, output_dir: str) -> str:
    try:
        images = convert_from_path(input_pdf)
        if not images:
            raise ValueError("No pages found in PDF")

        if len(images) == 1:
            img_path = os.path.join(output_dir, "page_1.jpg")
            images[0].save(img_path, "JPEG")
            return img_path

        zip_path = os.path.join(output_dir, "pdf_pages.zip")
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for i, image in enumerate(images):
                img_name = f"page_{i + 1}.jpg"
                img_path = os.path.join(output_dir, img_name)
                image.save(img_path, "JPEG")
                zipf.write(img_path, arcname=img_name)
        return zip_path
    except Exception as e:
        raise RuntimeError(f"PDF to Image conversion failed: {e}")
