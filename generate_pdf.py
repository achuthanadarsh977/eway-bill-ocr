from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.lib.utils import simpleSplit

W, H = landscape(A4)   # 841 x 595 pt

# ── Palette ───────────────────────────────────────────────────────
C_BG     = HexColor("#1E1E2E")
C_ACCENT = HexColor("#5C9EFF")
C_WHITE  = HexColor("#FFFFFF")
C_GREY   = HexColor("#CCCCCC")
C_CARD   = HexColor("#2A2A3E")
C_GREEN  = HexColor("#4CAF50")
C_ORANGE = HexColor("#FF9800")
C_PURPLE = HexColor("#7E57C2")
C_TEAL   = HexColor("#26A69A")

OUT = r"C:\Users\SriniAchuthan\Documents\eway_bill_ocr_ts\Eway_Bill_OCR_Design.pdf"
c = rl_canvas.Canvas(OUT, pagesize=landscape(A4))


# ── Drawing helpers ────────────────────────────────────────────────

def bg(color=C_BG):
    c.setFillColor(color)
    c.rect(0, 0, W, H, fill=1, stroke=0)

def rect(x, y, w, h, color=C_CARD, stroke=0):
    c.setFillColor(color)
    c.rect(x, y, w, h, fill=1, stroke=stroke)

def text(txt_str, x, y, size=12, color=C_WHITE, bold=False, align="left", max_width=None):
    c.setFillColor(color)
    font = "Helvetica-Bold" if bold else "Helvetica"
    c.setFont(font, size)
    if max_width and len(txt_str) * size * 0.55 > max_width:
        lines = simpleSplit(txt_str, font, size, max_width)
        for i, line in enumerate(lines):
            if align == "center":
                c.drawCentredString(x, y - i * (size + 2), line)
            else:
                c.drawString(x, y - i * (size + 2), line)
    else:
        if align == "center":
            c.drawCentredString(x, y, txt_str)
        elif align == "right":
            c.drawRightString(x, y, txt_str)
        else:
            c.drawString(x, y, txt_str)

def divider(y, color=C_ACCENT, x0=30, x1=None):
    if x1 is None:
        x1 = W - 30
    c.setStrokeColor(color)
    c.setLineWidth(1.5)
    c.line(x0, y, x1, y)

def top_bar(label, color=C_ACCENT):
    rect(0, H - 40, W, 40, color)
    text(label, 25, H - 26, size=14, bold=True, color=C_WHITE)

def bullets(items, x, y, size=11, color=C_GREY, line_h=17):
    for item in items:
        if item == "":
            y -= line_h // 2
            continue
        text(f"  {item}", x, y, size=size, color=color)
        y -= line_h
    return y


# ══════════════════════════════════════════════════════════════════
# SLIDE 1 — Title
# ══════════════════════════════════════════════════════════════════
bg()
rect(0, H - 40, W, 40, C_ACCENT)
text("OCR MODULE DESIGN", 25, H - 26, size=14, bold=True)

text("Eway Bill Document Parser", W / 2, H - 130, size=36, bold=True, align="center")
divider(H - 155)
text("Converts Eway Bill PDFs  →  Structured JSON automatically",
     W / 2, H - 180, size=16, color=C_GREY, align="center")

metas = [("Prepared by", "Adarsh"), ("Date", "04-Jun-2026"), ("Status", "Draft — Pending Review")]
for i, (lbl, val) in enumerate(metas):
    bx = 130 + i * 200
    rect(bx, 80, 180, 80, C_CARD)
    text(lbl, bx + 10, 143, size=10, color=C_ACCENT, bold=True)
    text(val, bx + 10, 122, size=13, color=C_WHITE)

c.showPage()

# ══════════════════════════════════════════════════════════════════
# SLIDE 2 — Objective
# ══════════════════════════════════════════════════════════════════
bg()
top_bar("01  |  OBJECTIVE")
text("What are we building?", 30, H - 65, size=22, bold=True)
divider(H - 85)

goals = [
    "Accept an Eway Bill PDF as input",
    "Automatically detect if PDF is digital or scanned",
    "Extract all relevant fields using OCR",
    "Return structured data in JSON format",
    "Plug into any downstream application — fully independent module",
]
for i, goal in enumerate(goals):
    y = H - 115 - i * 55
    rect(30, y - 8, 36, 36, C_ACCENT)
    text(str(i + 1), 48, y + 4, size=14, bold=True, align="center")
    text(goal, 80, y + 12, size=15, color=C_WHITE)

c.showPage()

# ══════════════════════════════════════════════════════════════════
# SLIDE 3 — Data Flow
# ══════════════════════════════════════════════════════════════════
bg()
top_bar("02  |  HIGH-LEVEL DATA FLOW")

stages = [
    ("Input PDF",   C_CARD,   "📄"),
    ("PDF Loader",  C_ACCENT, "🔍"),
    ("OCR Engine",  C_PURPLE, "⚙"),
    ("Parser",      C_TEAL,   "📋"),
    ("Formatter",   C_GREEN,  "📤"),
]
sub = ["", "Detect type\n(digital/scanned)", "Extract\nraw text", "Pull fields\nvia regex", "JSON / CSV\noutput"]

bw, bh = 130, 110
gap = 18
total = len(stages) * bw + (len(stages) - 1) * gap
sx = (W - total) / 2

for i, ((name, col, icon), sublabel) in enumerate(zip(stages, sub)):
    bx = sx + i * (bw + gap)
    by = H / 2 - bh / 2
    rect(bx, by, bw, bh, col)
    text(icon, bx + bw / 2, by + bh - 22, size=22, align="center")
    text(name, bx + bw / 2, by + bh - 52, size=12, bold=True, align="center")
    if sublabel:
        for j, ln in enumerate(sublabel.split("\n")):
            text(ln, bx + bw / 2, by - 20 - j * 14, size=10, color=C_GREY, align="center")
    if i < len(stages) - 1:
        ax = bx + bw + 4
        ay = by + bh / 2
        c.setFillColor(C_ACCENT)
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(ax + gap / 2, ay - 5, "▶")

c.showPage()

# ══════════════════════════════════════════════════════════════════
# SLIDE 4 — Module 1 & 2
# ══════════════════════════════════════════════════════════════════
bg()
top_bar("03  |  MODULES 1 & 2")

for col_i, (title, items, color) in enumerate([
    ("Module 1 — PDF Loader", [
        "Load the PDF from file path",
        "Attempt text extraction with pdf-parse",
        "Text > 50 chars  →  Digital PDF",
        "Text empty / minimal  →  Scanned PDF",
        "",
        "Output fields:",
        "  path, filename, numPages,",
        "  isDigital, rawBuffer, pagesText[]",
    ], C_ACCENT),
    ("Module 2 — OCR Engine", [
        "Routes based on PDF type:",
        "",
        "Digital PDF:",
        "  → Return text directly (fast)",
        "",
        "Scanned PDF:",
        "  → Convert pages to images",
        "  → Run tesseract.js (WASM-based)",
        "  → Return extracted text",
    ], C_PURPLE),
]):
    bx = 30 + col_i * 415
    rect(bx, 60, 400, H - 115, C_CARD)
    rect(bx, H - 115, 400, 36, color)
    text(title, bx + 12, H - 95, size=14, bold=True, color=C_WHITE)
    divider(H - 115, color=color, x0=bx, x1=bx + 400)
    bullets(items, bx + 15, H - 140, size=12)

c.showPage()

# ══════════════════════════════════════════════════════════════════
# SLIDE 5 — Module 3 (Parser)
# ══════════════════════════════════════════════════════════════════
bg()
top_bar("04  |  MODULE 3 — PARSER")
text("Fields extracted from every Eway Bill", 30, H - 58, size=16, bold=True)
divider(H - 76)

sections = [
    ("EWB Details",   ["EWB Number", "EWB Date", "Valid Until", "Txn Type", "Doc No & Date", "Value of Goods", "IRN"],
     C_ACCENT),
    ("From Party",    ["GSTIN", "Company Name", "Place", "State", "Pincode"],
     C_TEAL),
    ("To Party",      ["GSTIN", "Company Name", "Place", "State", "Pincode"],
     C_PURPLE),
    ("Item Details",  ["HSN Code", "Product Desc."],
     C_ORANGE),
    ("Transporter",   ["Transporter GSTIN", "Name", "Vehicle No.", "Mode"],
     C_GREEN),
]
# column width: leave 30px margin each side, 5 columns, 5px gap between
cw = (W - 60) / len(sections) - 5
HEADER_TOP = H - 108   # top of colored column headers (safely below title+divider)
CARD_BOT   = 50        # bottom of cards
CARD_H     = HEADER_TOP - CARD_BOT + 30  # includes header strip

for i, (sec, fields, col) in enumerate(sections):
    bx = 30 + i * (cw + 5)
    rect(bx, CARD_BOT, cw, CARD_H, C_CARD)           # card body
    rect(bx, HEADER_TOP, cw, 30, col)                 # colored header strip
    text(sec, bx + cw / 2, HEADER_TOP + 10, size=11, bold=True, align="center")
    bullets(fields, bx + 8, HEADER_TOP - 12, size=11, line_h=19)

c.showPage()

# ══════════════════════════════════════════════════════════════════
# SLIDE 6 — Module 4 & 5
# ══════════════════════════════════════════════════════════════════
bg()
top_bar("05  |  MODULES 4 & 5")

for col_i, (title, items, color) in enumerate([
    ("Module 4 — Formatter", [
        "Saves parsed data to disk",
        "",
        "JSON  (primary)",
        "  → Pretty-printed nested structure",
        "  → Used by downstream apps",
        "",
        "CSV  (secondary)",
        "  → Flattened single-row format",
        "  → For manual review / Excel",
        "",
        "Naming: {filename}_{timestamp}.json",
    ], C_TEAL),
    ("Module 5 — Main Entry Point", [
        "Wires all 4 modules together",
        "Accepts CLI arguments",
        "",
        "Commands:",
        "  ts-node main.ts <pdf>",
        "     → outputs JSON",
        "",
        "  ts-node main.ts <pdf> --csv",
        "     → also outputs CSV",
        "",
        "  ts-node main.ts <pdf> --raw",
        "     → prints raw text",
    ], C_GREEN),
]):
    bx = 30 + col_i * 415
    rect(bx, 60, 400, H - 115, C_CARD)
    rect(bx, H - 115, 400, 36, color)
    text(title, bx + 12, H - 95, size=14, bold=True, color=C_WHITE)
    divider(H - 115, color=color, x0=bx, x1=bx + 400)
    bullets(items, bx + 15, H - 140, size=12)

c.showPage()

# ══════════════════════════════════════════════════════════════════
# SLIDE 7 — Tech Stack
# ══════════════════════════════════════════════════════════════════
bg()
top_bar("06  |  TECHNOLOGY STACK")

stack = [
    ("TypeScript",   "Language",               "Type safety, better maintainability"),
    ("Node.js",      "Runtime",                "Cross-platform, no server needed"),
    ("pdf-parse",    "Digital PDF Extraction", "Pure JS — no system dependencies"),
    ("tesseract.js", "Scanned PDF OCR",        "WASM-based — no system install needed"),
    ("JSON + CSV",   "Output Formats",         "JSON for apps, CSV for manual review"),
]
row_h = 70
gap   = 8
# First row top = H - 55 = 540, well below top bar at H-40=555
for i, (tech, role, reason) in enumerate(stack):
    y = H - 55 - row_h - i * (row_h + gap)   # top of each row at H-55 and stepping down
    rect(30,  y, 130, row_h, C_ACCENT)
    text(tech, 95,  y + row_h / 2 - 6, size=13, bold=True, align="center")
    rect(168,  y, 260, row_h, C_CARD)
    text(role, 178, y + row_h / 2 - 6, size=12, color=C_GREY)
    rect(436,  y, 375, row_h, C_CARD)
    text(reason, 446, y + row_h / 2 - 6, size=12, color=C_WHITE)

text("Why no cloud API?  →  Free, local, no rate limits, sustainable at any volume",
     W / 2, 22, size=12, color=C_ACCENT, align="center")

c.showPage()

# ══════════════════════════════════════════════════════════════════
# SLIDE 8 — Build Plan
# ══════════════════════════════════════════════════════════════════
bg()
top_bar("07  |  INCREMENTAL BUILD PLAN")

phases = [
    ("Phase 1", "PDF Loader + Digital text extraction",    "DONE",    C_GREEN),
    ("Phase 2", "Parser — all Eway Bill fields via regex", "DONE",    C_GREEN),
    ("Phase 3", "JSON + CSV formatter",                   "DONE",    C_GREEN),
    ("Phase 4", "Scanned PDF support via tesseract.js",   "PENDING", C_ORANGE),
    ("Phase 5", "Batch processing — folder of PDFs",      "PENDING", C_ORANGE),
    ("Phase 6", "REST API wrapper (optional)",            "PENDING", C_ORANGE),
]
rh  = 68
gap = 7
# 6 rows × (68+7) − 7 = 443 pt; first row top at H-55=540
for i, (phase, desc, status, col) in enumerate(phases):
    y = H - 55 - rh - i * (rh + gap)
    rect(30,  y, 100, rh, col)
    text(phase, 80,  y + rh / 2 - 6, size=12, bold=True, align="center")
    rect(138,  y, 570, rh, C_CARD)
    text(desc,  150, y + rh / 2 - 6, size=13, color=C_WHITE)
    rect(716,  y,  95, rh, col)
    text(status, 763, y + rh / 2 - 6, size=11, bold=True, align="center")

c.showPage()

# ══════════════════════════════════════════════════════════════════
# SLIDE 9 — Open Questions
# ══════════════════════════════════════════════════════════════════
bg()
top_bar("08  |  OPEN QUESTIONS FOR REVIEW")
# subtitle sits 15 pt below top bar
text("Seeking answers before Phase 4 implementation begins",
     30, H - 58, size=14, color=C_GREY)
divider(H - 75)

questions = [
    ("Q1", "Multi-item Eway Bills",
     "Should the module handle documents with multiple HSN codes / items per bill?"),
    ("Q2", "API vs CLI",
     "Do we need a REST API wrapper, or is CLI usage sufficient for now?"),
    ("Q3", "JSON Schema",
     "Should output JSON follow a specific schema already used in the system?"),
    ("Q4", "Future Document Types",
     "Are there more docs to handle — invoices, delivery challans, etc.?"),
]
qh  = 100
gap = 10
# 4 rows × (100+10) − 10 = 430 pt; fit inside 555−75−40 = 440 pt of content space
# first row top at H-90 = 505, just below divider at H-75=520
for i, (q, title, detail) in enumerate(questions):
    y = H - 90 - qh - i * (qh + gap)
    rect(30, y, 52, qh, C_ACCENT)
    text(q, 56, y + qh / 2 - 6, size=14, bold=True, align="center")
    rect(90, y, 721, qh, C_CARD)
    text(title,  104, y + qh - 22, size=14, bold=True, color=C_ACCENT)
    text(detail, 104, y + qh - 50, size=12, color=C_GREY, max_width=700)

c.showPage()

# ══════════════════════════════════════════════════════════════════
# SLIDE 10 — Summary
# ══════════════════════════════════════════════════════════════════
bg()
rect(0, H - 40, W, 40, C_ACCENT)

# Title — 20 pt below top bar
text("Ready for Review", W / 2, H - 95, size=38, bold=True, align="center")
divider(H - 128)
text("Phases 1–3 are complete and working on real Eway Bill PDFs",
     W / 2, H - 155, size=16, color=C_GREY, align="center")

# Stat cards — centred, 15 pt below subtitle
stats = [
    ("5 Modules",        "Independent, plug-and-play"),
    ("2 Output Formats", "JSON + CSV"),
    ("0 Cloud APIs",     "Fully local, sustainable"),
    ("3 Phases Done",    "Working on real PDFs today"),
]
bw2   = 175
gap2  = 14
card_h2 = 140
total2  = len(stats) * bw2 + (len(stats) - 1) * gap2
sx2     = (W - total2) / 2
card_y2 = H - 155 - 20 - card_h2    # 20 pt gap below subtitle

for i, (stat, lbl) in enumerate(stats):
    bx = sx2 + i * (bw2 + gap2)
    rect(bx, card_y2, bw2, card_h2, C_CARD)
    # accent top strip
    rect(bx, card_y2 + card_h2 - 6, bw2, 6, C_ACCENT)
    text(stat, bx + bw2 / 2, card_y2 + card_h2 / 2 + 14,
         size=17, bold=True, color=C_ACCENT, align="center")
    text(lbl,  bx + bw2 / 2, card_y2 + card_h2 / 2 - 14,
         size=12, color=C_GREY, align="center")

text("Prepared by Adarsh  |  04-Jun-2026  |  Pending Manager Review",
     W / 2, 22, size=11, color=C_GREY, align="center")

c.showPage()

# ── Save ──────────────────────────────────────────────────────────
c.save()
print(f"PDF saved: {OUT}")
