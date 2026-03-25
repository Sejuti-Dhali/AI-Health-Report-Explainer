import pdfplumber
import pytesseract
from PIL import Image
import io


def extract_text_from_pdf(file_bytes: bytes) -> str:
    text = ""
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()


def extract_text_from_image(file_bytes: bytes) -> str:
    image = Image.open(io.BytesIO(file_bytes))
    text = pytesseract.image_to_string(image)
    return text.strip()


def extract_text(file_bytes: bytes, filename: str) -> str:
    filename_lower = filename.lower()
    if filename_lower.endswith(".pdf"):
        return extract_text_from_pdf(file_bytes)
    elif filename_lower.endswith((".png", ".jpg", ".jpeg", ".tiff", ".bmp")):
        return extract_text_from_image(file_bytes)
    else:
        raise ValueError(f"Unsupported file type: {filename}")
