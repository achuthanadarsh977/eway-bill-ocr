# OCR Module Design — Eway Bill Document Parser
**Prepared by:** Adarsh  
**Date:** 04-Jun-2026  
**Status:** Draft — Pending Review  

---

## 1. Objective

Build an **independent, reusable OCR module** that:
- Accepts an Eway Bill PDF as input
- Extracts all relevant fields using OCR
- Returns structured output in **JSON format**
- Can be plugged into any part of the system wherever documents need to be parsed

---

## 2. High-Level Data Flow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│             │     │             │     │             │     │             │     │             │
│  Input PDF  │────▶│ PDF Loader  │────▶│ OCR Engine  │────▶│   Parser    │────▶│  Formatter  │
│             │     │             │     │             │     │             │     │             │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
                          │                    │                    │                    │
                    Detect type          Extract raw          Pull fields          JSON / CSV
                  (digital/scanned)        text               via regex             output
```

---

## 3. Module Breakdown

### Module 1 — PDF Loader (`pdfLoader.ts`)
**Responsibility:** Load the PDF file and detect whether it is digital or scanned.

**Input:** File path to PDF  
**Output:** PDF metadata object  

```
PDFInfo {
  path        : string       -- full file path
  filename    : string       -- file name
  numPages    : number       -- total pages
  isDigital   : boolean      -- true if embedded text found
  rawBuffer   : Buffer       -- raw PDF bytes
  pagesText   : string[]     -- text per page (if digital)
}
```

**Logic:**
- Use `pdf-parse` to attempt text extraction
- If extracted text length > 50 characters → mark as Digital
- If extracted text is empty/minimal → mark as Scanned

---

### Module 2 — OCR Engine (`ocrEngine.ts`)
**Responsibility:** Extract raw text from the PDF based on its type.

**Input:** PDFInfo object  
**Output:** Raw text string  

```
Digital PDF  ──▶  Return text directly from pdfLoader (no OCR needed)
Scanned PDF  ──▶  Convert pages to images ──▶ Run tesseract.js ──▶ Return text
```

**Tools used:**
- Digital: `pdf-parse` (already loaded by pdfLoader)
- Scanned: `tesseract.js` (WASM-based, no system install)

---

### Module 3 — Parser (`parser.ts`)
**Responsibility:** Extract specific Eway Bill fields from raw text using regex patterns.

**Input:** Raw text string  
**Output:** Structured EwayBillData object  

**Fields extracted:**

```
EwayBillData {
  ewb_details {
    ewb_number           -- 12-digit EWB number
    ewb_date             -- date + time of generation
    valid_until          -- expiry date
    transaction_type     -- Regular / Bill To Ship To etc.
    document_number      -- invoice number
    document_date        -- invoice date
    value_of_goods       -- total invoice value
    reason_for_transport -- Outward/Inward supply type
    irn                  -- Invoice Reference Number (if present)
  }
  from_party {
    gstin                -- supplier GSTIN (15 chars)
    name                 -- supplier company name
    place                -- dispatch city
    state                -- dispatch state
    pincode              -- 6-digit PIN
  }
  to_party {
    gstin                -- recipient GSTIN
    name                 -- recipient company name
    place                -- delivery city
    state                -- delivery state
    pincode              -- 6-digit PIN
  }
  item_details {
    hsn_code             -- 6-8 digit HSN code
    product_description  -- product/goods description
  }
  transporter_details {
    transporter_gstin    -- transporter GSTIN
    transporter_name     -- transporter company name
    vehicle_number       -- vehicle registration number
    transport_mode       -- Road / Rail / Air / Ship
  }
}
```

---

### Module 4 — Formatter (`formatter.ts`)
**Responsibility:** Save the parsed data in the required output format.

**Input:** EwayBillData object + output directory + filename  
**Output:** Saved file path  

**Formats supported:**
- `JSON` — pretty-printed, nested structure (primary)
- `CSV` — flattened single-row (secondary, for spreadsheet use)

**Output file naming:**
```
{original_filename}_{YYYY-MM-DDTHH-MM-SS}.json
{original_filename}_{YYYY-MM-DDTHH-MM-SS}.csv
```

---

### Module 5 — Main Entry Point (`main.ts`)
**Responsibility:** Wire all modules together. Accept CLI arguments and run the pipeline end to end.

**Usage:**
```
npx ts-node src/main.ts <pdf_path>           -- outputs JSON
npx ts-node src/main.ts <pdf_path> --csv     -- also outputs CSV
npx ts-node src/main.ts <pdf_path> --raw     -- prints raw extracted text
```

**Pipeline:**
```
1. Parse CLI arguments
2. Call pdfLoader  → get PDFInfo
3. Call ocrEngine  → get raw text
4. Call parser     → get structured data
5. Call formatter  → save JSON (and CSV if requested)
6. Print output to console
```

---

## 4. Project Folder Structure

```
eway_bill_ocr_ts/
├── src/
│   ├── main.ts                 ← Entry point / CLI
│   └── modules/
│       ├── pdfLoader.ts        ← Module 1: Load + detect PDF type
│       ├── ocrEngine.ts        ← Module 2: Extract raw text
│       ├── parser.ts           ← Module 3: Parse Eway Bill fields
│       └── formatter.ts        ← Module 4: Save JSON / CSV
├── output/                     ← Generated JSON and CSV files go here
├── samples/                    ← Sample Eway Bill PDFs for testing
├── package.json
├── tsconfig.json
├── RESEARCH.md                 ← Tool research document
└── DESIGN.md                   ← This document
```

---

## 5. Technology Stack

| Component | Technology | Reason |
|-----------|-----------|--------|
| Language | TypeScript | Type safety, better maintainability |
| Runtime | Node.js | Cross-platform, team familiarity |
| Digital PDF extraction | `pdf-parse` | Pure JS, no system dependencies |
| Scanned PDF OCR | `tesseract.js` | WASM-based, no system install needed |
| Output | JSON + CSV | JSON for downstream apps, CSV for manual review |

---

## 6. Incremental Build Plan

| Phase | What gets built | Done? |
|-------|----------------|-------|
| Phase 1 | PDF Loader + basic text extraction (digital PDFs) | ✅ |
| Phase 2 | Parser with regex for all Eway Bill fields | ✅ |
| Phase 3 | JSON + CSV formatter | ✅ |
| Phase 4 | Scanned PDF support via tesseract.js | 🔲 |
| Phase 5 | Batch processing (folder of PDFs) | 🔲 |
| Phase 6 | REST API wrapper (optional — so other apps can call it via HTTP) | 🔲 |

---

## 7. Assumptions & Constraints

- Eway Bills are sourced from the GST portal → mostly digital PDFs
- Output JSON schema is fixed to the fields listed in Section 3
- No cloud API dependency — fully local processing
- Module is independent and stateless — no database required
- For scanned PDFs, accuracy depends on scan quality

---

## 8. Open Questions for Review

1. Should the module also handle **multi-item Eway Bills** (multiple HSN codes per document)?
2. Do we need a **REST API** wrapper, or is CLI usage sufficient for now?
3. Should the output JSON follow a **specific schema** already used in the system?
4. Are there more document types beyond Eway Bills to handle in future (e.g. invoices, delivery challans)?
