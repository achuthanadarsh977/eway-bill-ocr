import "dotenv/config";
import express from "express";
import helmet from "helmet";
import multer from "multer";
import path from "path";
import os from "os";
import fs from "fs";
import { loadPdf } from "./modules/pdfLoader";
import { extractText } from "./modules/ocrEngine";
import { parseEwayBill } from "./modules/parser";

const app = express();
const PORT = Number(process.env.PORT) || 3000;

// Security headers — relaxed CSP so Tailwind CDN loads in the UI
app.use(
  helmet({
    contentSecurityPolicy: {
      directives: {
        defaultSrc: ["'self'"],
        scriptSrc: ["'self'", "https://cdn.tailwindcss.com", "'unsafe-inline'"],
        styleSrc: ["'self'", "'unsafe-inline'"],
        imgSrc: ["'self'", "data:"],
      },
    },
  })
);

app.use(express.static(path.join(__dirname, "..", "public")));

// Health check — used by hosting platforms (Railway, Render, etc.)
app.get("/health", (_req, res) => {
  res.json({ status: "ok", timestamp: new Date().toISOString() });
});

const upload = multer({
  dest: os.tmpdir(),
  fileFilter: (_req, file, cb) => {
    if (file.mimetype === "application/pdf" || file.originalname.toLowerCase().endsWith(".pdf")) {
      cb(null, true);
    } else {
      cb(new Error("Only PDF files are allowed"));
    }
  },
  limits: { fileSize: 20 * 1024 * 1024 },
});

app.post("/api/ocr", upload.single("pdf"), async (req, res) => {
  if (!req.file) {
    res.status(400).json({ error: "No PDF file uploaded" });
    return;
  }

  const tmpPath = req.file.path;
  const originalName = req.file.originalname;

  try {
    const pdfInfo = await loadPdf(tmpPath);
    const rawText = await extractText(pdfInfo);
    const parsed = parseEwayBill(rawText);

    res.json({
      success: true,
      filename: originalName,
      numPages: pdfInfo.numPages,
      pdfType: pdfInfo.isDigital ? "Digital" : "Scanned",
      data: parsed,
    });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  } finally {
    fs.unlink(tmpPath, () => {});
  }
});

app.listen(PORT, () => {
  console.log(`\n  Eway Bill OCR Web UI`);
  console.log(`  Running at http://localhost:${PORT}\n`);
});
