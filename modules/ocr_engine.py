import fitz  # PyMuPDF
import io

try:
    import easyocr
    import numpy as np
    from PIL import Image, ImageEnhance, ImageFilter
    _EASYOCR_AVAILABLE = True
except ImportError:
    _EASYOCR_AVAILABLE = False

_reader = None


def _get_reader():
    if not _EASYOCR_AVAILABLE:
        raise RuntimeError("EasyOCR is not installed. Only digital PDFs are supported on this server.")
    global _reader
    if _reader is None:
        print("Loading EasyOCR model (first time only)...")
        _reader = easyocr.Reader(["en"], gpu=False)
    return _reader


def _preprocess_for_ocr(img):
    """
    Upscale, denoise, and enhance contrast so EasyOCR reads
    phone-photos and low-DPI scans accurately.
    """
    gray = img.convert("L")

    # Upscale to at least 2000 px wide — EasyOCR needs adequate resolution
    w, h = gray.size
    if w < 2000:
        scale = 2000 / w
        gray = gray.resize((int(w * scale), int(h * scale)), Image.LANCZOS)

    # Light denoise then sharpen
    gray = gray.filter(ImageFilter.MedianFilter(size=3))
    gray = ImageEnhance.Sharpness(gray).enhance(2.0)
    gray = ImageEnhance.Contrast(gray).enhance(1.8)

    return np.array(gray.convert("RGB"))


def _results_to_text(results: list) -> str:
    """
    Convert EasyOCR detail=1 results to line-ordered text.
    Sorts items by their vertical position, groups into lines,
    then sorts each line left-to-right — preserves field layout.
    """
    if not results:
        return ""

    items = []
    for bbox, text, _conf in results:
        y_top    = min(pt[1] for pt in bbox)
        y_bottom = max(pt[1] for pt in bbox)
        x_left   = min(pt[0] for pt in bbox)
        height   = y_bottom - y_top
        items.append((y_top, y_bottom, height, x_left, text.strip()))

    if not items:
        return ""

    # Median text height used as line-grouping tolerance
    median_h = sorted(items, key=lambda x: x[2])[len(items) // 2][2]
    tolerance = max(median_h * 0.6, 8)

    items.sort(key=lambda x: x[0])

    lines = []
    current = [items[0]]
    for item in items[1:]:
        if item[0] - current[-1][0] <= tolerance:
            current.append(item)
        else:
            current.sort(key=lambda x: x[3])          # left → right
            lines.append("  ".join(t for *_, t in current))
            current = [item]
    if current:
        current.sort(key=lambda x: x[3])
        lines.append("  ".join(t for *_, t in current))

    return "\n".join(lines)


def extract_text_digital(pdf_info: dict) -> str:
    return "\n".join(pdf_info["pages_text"])


def extract_text_scanned(pdf_path: str) -> str:
    """Convert each PDF page to image, preprocess, then OCR."""
    reader = _get_reader()
    doc = fitz.open(pdf_path)
    full_text = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        mat = fitz.Matrix(2.0, 2.0)
        pix = page.get_pixmap(matrix=mat)
        img = Image.open(io.BytesIO(pix.tobytes("png")))

        img_array = _preprocess_for_ocr(img)
        results   = reader.readtext(img_array, detail=1)
        full_text.append(_results_to_text(results))
        print(f"  Page {page_num + 1} OCR done.")

    doc.close()
    return "\n".join(full_text)


def extract_text_from_images(images: list) -> str:
    """Run EasyOCR on PIL Image objects (uploaded TIFF/PNG/JPG/BMP)."""
    reader = _get_reader()
    full_text = []

    for i, img in enumerate(images):
        img_array = _preprocess_for_ocr(img)
        results   = reader.readtext(img_array, detail=1)
        full_text.append(_results_to_text(results))
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
