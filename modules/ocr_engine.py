import fitz
import io
from PIL import Image, ImageEnhance, ImageFilter

try:
    import pytesseract
    _TESSERACT_AVAILABLE = True
except ImportError:
    _TESSERACT_AVAILABLE = False


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
    if not _TESSERACT_AVAILABLE:
        raise RuntimeError("Tesseract OCR is not installed on this server.")
    processed = _preprocess(img)
    return pytesseract.image_to_string(processed, config="--psm 6")


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
        print("Image file detected — running Tesseract OCR.")
        return extract_text_from_images(pdf_info["images"])
    elif pdf_info["is_digital"]:
        print("Digital PDF detected — extracting text directly.")
        return extract_text_digital(pdf_info)
    else:
        print("Scanned PDF detected — running Tesseract OCR.")
        return extract_text_scanned(pdf_info["path"])
