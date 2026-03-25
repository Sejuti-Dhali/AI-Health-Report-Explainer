import io
from typing import Optional


def extract_text_from_file(file_bytes: bytes, content_type: str) -> Optional[str]:
    """
    Dispatch to the correct extractor based on MIME type.
    Returns extracted plain text, or None on failure.
    """
    if content_type == "application/pdf":
        return _extract_from_pdf(file_bytes)
    elif content_type in ["image/png", "image/jpeg"]:
        return _extract_from_image(file_bytes)
    return None


def _extract_from_pdf(file_bytes: bytes) -> str:
    try:
        import pdfplumber

        text_parts = []
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
        return "\n".join(text_parts)
    except Exception as e:
        print(f"[OCR] PDF extraction error: {e}")
        return ""


def _extract_from_image(file_bytes: bytes) -> str:
    try:
        import pytesseract
        from PIL import Image

        image = Image.open(io.BytesIO(file_bytes))
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        print(f"[OCR] Image extraction error: {e}")
        return ""