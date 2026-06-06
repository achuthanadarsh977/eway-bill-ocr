import { createWorker } from "tesseract.js";
import { PdfInfo } from "./pdfLoader";
import Jimp from "jimp";

// Extract text directly from a digital PDF
function extractDigital(pdfInfo: PdfInfo): string {
  return pdfInfo.pagesText.join("\n");
}

// Run Tesseract OCR on a provided image file (for scanned PDFs)
async function extractFromImage(imagePath: string): Promise<string> {
  const worker = await createWorker("eng");
  const { data } = await worker.recognize(imagePath);
  await worker.terminate();
  return data.text;
}

// For scanned PDFs: user must provide image paths instead
async function extractScanned(pdfInfo: PdfInfo): Promise<string> {
  console.log("\n  NOTE: Scanned PDF detected.");
  console.log("  For scanned documents, convert each page to a PNG/JPG image");
  console.log("  and pass the image path instead of the PDF.\n");
  console.log("  Attempting basic text recovery from PDF binary...");

  // Try to extract any embedded text fragments from the raw buffer
  const raw = pdfInfo.rawBuffer.toString("latin1");
  const fragments = raw.match(/\(([^\)]{3,80})\)/g) || [];
  const recovered = fragments
    .map((f) => f.slice(1, -1))
    .filter((f) => /[a-zA-Z0-9]/.test(f))
    .join(" ");

  return recovered || "[No readable text found — please provide image files for scanned PDFs]";
}

export async function extractText(pdfInfo: PdfInfo): Promise<string> {
  if (pdfInfo.isDigital) {
    console.log("Digital PDF detected — extracting text directly.");
    return extractDigital(pdfInfo);
  } else {
    return extractScanned(pdfInfo);
  }
}

// Standalone function: run OCR on an image file directly
export async function extractFromImageFile(imagePath: string): Promise<string> {
  console.log(`Running Tesseract OCR on image: ${imagePath}`);
  const worker = await createWorker("eng");
  const { data } = await worker.recognize(imagePath);
  await worker.terminate();
  return data.text;
}
