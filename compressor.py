import os
import pymupdf
from io import BytesIO
from PIL import Image


def get_file_size_kb(file_path):
    size_bytes = os.path.getsize(file_path)
    size_kb = size_bytes / 1024
    return size_kb

def compress_once(input_path, output_path, quality, max_size):
    doc = pymupdf.open(input_path)

    for page in doc:
        images = page.get_images(full=True)

        for image in images:
            xref = image[0]

            image_info = doc.extract_image(xref)
            image_bytes = image_info["image"]

            image_file = BytesIO(image_bytes)
            pil_image = Image.open(image_file)

            if pil_image.width > max_size or pil_image.height > max_size:
                pil_image.thumbnail((max_size, max_size))

            # JPEG не поддерживает некоторые режимы Pillow,
            # например RGBA, поэтому переводим в RGB
            if pil_image.mode != "RGB":
                pil_image = pil_image.convert("RGB")

            output_image = BytesIO()

            pil_image.save(
                output_image,
                format="JPEG",
                quality=quality
            )

            compressed_bytes = output_image.getvalue()

            if len(compressed_bytes) < len(image_bytes):
                page.replace_image(
                    xref,
                    stream=compressed_bytes
                )

    doc.save(output_path)
    doc.close()

    return get_file_size_kb(output_path)



def compress_pdf(input_path, output_path, target_kb):
    current_kb = get_file_size_kb(input_path)
    print("Исходный размер:", current_kb, "KB")

    if current_kb <= target_kb:
        return True, current_kb

    quality = 85
    max_size = 1600

    min_quality = 40
    min_size = 800

    success = False

    while True:
        new_size_kb = compress_once(
            input_path,
            output_path,
            quality,
            max_size
        )
        print("Попытка: quality =", [quality], "max_size =", [max_size], "Размер:", [new_size_kb])

        if new_size_kb <= target_kb:
            success = True
            break

        if quality > min_quality:
            quality -= 5
            continue

        if max_size > min_size:
            max_size -= 200
            quality = 85
            continue

        break

    print("Результат сжатия:", [new_size_kb])
    return success, new_size_kb