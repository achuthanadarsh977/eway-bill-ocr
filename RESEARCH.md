# OCR Tool Research — Eway Bill Document Parser
**Prepared by:** Adarsh  
**Date:** 04-Jun-2026  
**Purpose:** Research on available free OCR tools to build an independent OCR module for Eway Bill documents

---

## 1. Problem Statement

We receive Eway Bill documents (PDFs) as part of our logistics workflow. Currently these are processed manually. The goal is to build an **independent OCR module** that:
- Takes an Eway Bill PDF as input
- Reads the document using OCR
- Outputs structured data in **JSON format**
- Can be plugged into any downstream application

---

## 2. Types of PDFs We Deal With

| Type | Description | How to handle |
|------|-------------|---------------|
| **Digital PDF** | Generated electronically (e.g. GST portal) — text is embedded | Direct text extraction, no OCR needed |
| **Scanned PDF** | Physical document scanned to PDF — text is in image form | Full OCR required |

Most Eway Bills from the GST portal are **digital PDFs**, which makes text extraction faster and more accurate.

---

## 3. OCR Tools Evaluated

### 3.1 Python Libraries

| Tool | Type | Cost | Accuracy | Windows Support | Notes |
|------|------|------|----------|-----------------|-------|
| **pdfplumber** | Digital PDF text extractor | Free | High (for digital PDFs) | Yes | Best for digital PDFs, no OCR needed |
| **PyMuPDF (fitz)** | Digital PDF text extractor | Free | High | Yes | Fast, reliable, widely used |
| **Tesseract OCR** | Open-source OCR engine | Free | Medium-High | Yes (needs install) | Industry standard, requires system install |
| **pytesseract** | Python wrapper for Tesseract | Free | Medium-High | Yes | Requires Tesseract installed separately |
| **EasyOCR** | Deep learning OCR | Free | High | Yes | No system install needed, GPU optional |
| **PaddleOCR** | Deep learning OCR by Baidu | Free | Very High | Yes | More accurate but heavier model |
| **pdf2image** | PDF to image converter | Free | N/A | Yes (needs Poppler) | Used with Tesseract for scanned PDFs |

### 3.2 JavaScript / TypeScript Libraries (Node.js)

| Tool | Type | Cost | Accuracy | Windows Support | Notes |
|------|------|------|----------|-----------------|-------|
| **pdf-parse** | Digital PDF text extractor | Free | High (for digital PDFs) | Yes | Pure JS, no native build needed |
| **pdfjs-dist** | Mozilla PDF.js | Free | High | Yes | Pure JS, widely used |
| **tesseract.js** | Tesseract OCR in WASM | Free | Medium-High | Yes | Pure JS, no system install needed |
| **node-tesseract-ocr** | Node wrapper for Tesseract | Free | Medium-High | Yes | Requires Tesseract system install |
| **canvas** | PDF page rendering | Free | N/A | Needs C++ build tools | Required for pdfjs scanned rendering |

---

## 4. Tool Comparison Matrix

| Criteria | pdfplumber / PyMuPDF | EasyOCR | Tesseract / pytesseract | tesseract.js | pdf-parse |
|----------|---------------------|---------|------------------------|--------------|-----------|
| Cost | Free | Free | Free | Free | Free |
| Works for digital PDFs | Yes | Overkill | Overkill | Overkill | Yes |
| Works for scanned PDFs | No | Yes | Yes | Yes | No |
| Accuracy | Very High | High | Medium | Medium | Very High |
| Setup difficulty | Easy | Easy | Medium (system install) | Easy | Easy |
| Speed | Very Fast | Slow (model load) | Medium | Medium | Very Fast |
| Windows compatible | Yes | Yes | Yes | Yes | Yes |
| No system dependencies | Yes | Yes | No | Yes | Yes |
| Language | Python | Python | Python | JavaScript | JavaScript |

---

## 5. Recommendation

### For Python
- **Primary:** `PyMuPDF (fitz)` — fast, reliable text extraction for digital PDFs
- **Fallback (scanned):** `EasyOCR` — already installed on the machine, no extra system setup

### For TypeScript / Node.js
- **Primary:** `pdf-parse` — pure JS, works without any native build tools
- **Fallback (scanned):** `tesseract.js` — pure WASM-based OCR, no system install needed

### Why not Tesseract (system)?
Requires system-level installation and C++ build tools on Windows, which adds setup overhead and makes the tool harder to deploy.

### Why not PaddleOCR?
Very accurate but heavy — large model size, slower startup. Overkill for structured Eway Bill PDFs which are mostly digital.

---

## 6. Sustainable Approach (as discussed)

The previous approach used free cloud APIs which are not sustainable (rate limits, downtime, cost at scale). The recommended approach:

- **Self-contained module** with no dependency on external APIs
- Uses **open-source libraries** that run locally
- Can be containerized (Docker) for deployment
- No per-call cost regardless of volume

---

## 7. Summary Decision

| Layer | Technology |
|-------|-----------|
| Language | TypeScript (Node.js) |
| Digital PDF extraction | `pdf-parse` |
| Scanned PDF OCR | `tesseract.js` |
| Output format | JSON (primary), CSV (secondary) |
| Architecture | Modular — plug-and-play |
