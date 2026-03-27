import io
import os
from typing import Optional

import numpy as np


def extract_text_from_file(file_bytes: bytes, content_type: str) -> Optional[str]:
    """
    Dispatch to the correct extractor based on MIME type.
    Supports PDF and image files.
    """
    print(f"[OCR] content_type={content_type}, bytes={len(file_bytes)}")

    if content_type == "application/pdf":
        return _extract_from_pdf(file_bytes)

    if content_type in ["image/png", "image/jpeg", "image/jpg"]:
        return _extract_from_image(file_bytes)

    return None


def _extract_from_pdf(file_bytes: bytes) -> str:
    try:
        import pdfplumber

        text_parts = []
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for i, page in enumerate(pdf.pages):
                page_text = page.extract_text()
                print(f"[OCR][PDF] page={i+1}, chars={len(page_text) if page_text else 0}")
                if page_text:
                    text_parts.append(page_text)

        combined = "\n".join(text_parts)
        print(f"[OCR][PDF] total_chars={len(combined)}")
        return combined

    except Exception as e:
        print(f"[OCR] PDF extraction error: {e}")
        return ""


def _configure_tesseract():
    import pytesseract

    candidates = [
        os.getenv("TESSERACT_CMD"),
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    ]

    for path in candidates:
        if path and os.path.exists(path):
            pytesseract.pytesseract.tesseract_cmd = path
            print(f"[OCR] Using Tesseract: {path}")
            return

    print("[OCR] Warning: Tesseract executable path not found automatically.")


def _preprocess_for_ocr(image):
    from PIL import Image
    import cv2

    # convert PIL -> numpy
    img = np.array(image)

    # handle RGBA / grayscale / RGB
    if len(img.shape) == 2:
        gray = img
    else:
        if img.shape[2] == 4:
            img = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    # enlarge small text
    gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

    # denoise
    gray = cv2.GaussianBlur(gray, (3, 3), 0)

    # threshold / binarize
    thresh = cv2.threshold(
        gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )[1]

    # PIL image ????
    return Image.fromarray(thresh)


def _extract_from_image(file_bytes: bytes) -> str:
    try:
        import pytesseract
        from PIL import Image

        _configure_tesseract()

        image = Image.open(io.BytesIO(file_bytes)).convert("RGB")
        processed = _preprocess_for_ocr(image)

        text = pytesseract.image_to_string(
            processed,
            config="--oem 3 --psm 6"
        )

        print(f"[OCR][IMG] total_chars={len(text)}")
        return text

    except Exception as e:
        print(f"[OCR] Image extraction error: {e}")
        return ""
