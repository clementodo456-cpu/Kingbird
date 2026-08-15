import os
from PIL import Image

def convert_images_to_pdf(image_paths: list, output_pdf: str) -> bool:
    try:
        if not image_paths:
            raise ValueError("No images provided")

        opened_images = []
        for path in image_paths:
            img = Image.open(path)
            if img.mode != "RGB":
                img = img.convert("RGB")
            opened_images.append(img)

        first_img = opened_images[0]
        rest_imgs = opened_images[1:] if len(opened_images) > 1 else []

        first_img.save(output_pdf, "PDF", resolution=100.0, save_all=True, append_images=rest_imgs)
        return os.path.exists(output_pdf)
    except Exception as e:
        raise RuntimeError(f"Images to PDF conversion failed: {e}")
