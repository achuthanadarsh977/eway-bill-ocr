import fitz  # PyMuPDF
from pathlib import Path
from PIL import Image


IMAGE_EXTENSIONS = {".tif", ".tiff", ".png", ".jpg", ".jpeg", ".bmp"}


def load_image(image_path: str) -> dict:
    """Load a scanned image file (TIFF/PNG/JPG/BMP) for OCR processing."""
    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    img = Image.open(image_path)
    pages = []

    # Support multi-page TIFFs (Windows Fax & Scan saves multi-page TIFFs)
    try:
        while True:
            pages.append(img.copy())
            img.seek(img.tell() + 1)
    except EOFError:
        pass

    if not pages:
        pages = [img]

    return {
        "path":       str(path),
        "filename":   path.name,
        "num_pages":  len(pages),
        "is_digital": False,
        "pages_text": [""] * len(pages),
        "images":     pages,   # PIL Image objects for OCR
    }


def load_pdf(pdf_path: str) -> dict:
    """Load PDF and detect if it is digital (text-based) or scanned (image-based)."""
    path = Path(pdf_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    doc = fitz.open(pdf_path)
    total_text = ""
    pages_text = []

    for page in doc:
        text = page.get_text().strip()
        pages_text.append(text)
        total_text += text

    doc.close()

    is_digital = len(total_text) > 50  # if meaningful text exists, it's digital

    return {
        "path": str(path),
        "filename": path.name,
        "num_pages": len(pages_text),
        "is_digital": is_digital,
        "pages_text": pages_text,
    }
