import fitz
import io
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter

_EASYOCR_AVAILABLE = False
try:
    import easyocr
    _EASYOCR_AVAILABLE = True
except ImportError:
    pass

_reader = None


def _get_reader():
    global _reader
    if not _EASYOCR_AVAILABLE:
        raise RuntimeError("EasyOCR is not installed. Run: pip install easyocr")
    if _reader is None:
        _reader = easyocr.Reader(['en'], gpu=False)
    return _reader


def _preprocess(img):
    gray = img.convert("L")
    w, h = gray.size
    if w < 2000:
        scale = 2000 / w
        gray = gray.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    gray = gray.filter(ImageFilter.MedianFilter(size=3))
    gray = ImageEnhance.Sharpness(gray).enhance(2.0)
    gray = ImageEnhance.Contrast(gray).enhance(1.8)
    return gray


def _ocr_image(img):
    processed = _preprocess(img)
    arr = np.array(processed)
    results = _get_reader().readtext(arr, detail=0, paragraph=True)
    return "\n".join(results)


def extract_text_digital(pdf_info: dict) -> str:
    return "\n".join(pdf_info["pages_text"])


def extract_text_scanned(pdf_path: str) -> str:
    doc = fitz.open(pdf_path)
    full_text = []
    for page_num in range(len(doc)):
        page = doc[page_num]
        pix = page.get_pixmap(matrix=fitz.Matrix(2.0, 2.0))
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        full_text.append(_ocr_image(img))
        print(f"  Page {page_num + 1} OCR done.")
    doc.close()
    return "\n".join(full_text)


def extract_text_from_images(images: list) -> str:
    full_text = []
    for i, img in enumerate(images):
        full_text.append(_ocr_image(img))
        print(f"  Image page {i + 1} OCR done.")
    return "\n".join(full_text)


def extract_text(pdf_info: dict) -> str:
    if "images" in pdf_info:
        print("Image file detected — running EasyOCR.")
        return extract_text_from_images(pdf_info["images"])
    elif pdf_info["is_digital"]:
        print("Digital PDF detected — extracting text directly.")
        return extract_text_digital(pdf_info)
    else:
        print("Scanned PDF detected — running EasyOCR.")
        return extract_text_scanned(pdf_info["path"])
