/**
 * Eway Bill OCR Tool (TypeScript)
 *
 * Usage:
 *   npx ts-node src/main.ts <path_to_pdf>
 *   npx ts-node src/main.ts <path_to_pdf> --csv
 *   npx ts-node src/main.ts <path_to_pdf> --raw
 */

import path from "path";
import { loadPdf } from "./modules/pdfLoader";
import { extractText } from "./modules/ocrEngine";
import { parseEwayBill } from "./modules/parser";
import { saveJson, saveCsv } from "./modules/formatter";

const OUTPUT_DIR = path.join(__dirname, "..", "output");

async function run() {
  const args = process.argv.slice(2);

  if (args.length === 0) {
    console.error("Usage: npx ts-node src/main.ts <pdf_path> [--csv] [--raw]");
    process.exit(1);
  }

  const pdfPath = args[0];
  const saveCsvFlag = args.includes("--csv");
  const showRaw = args.includes("--raw");

  console.log("\n" + "=".repeat(55));
  console.log("  Eway Bill OCR Tool (TypeScript)");
  console.log("=".repeat(55));
  console.log(`Input  : ${pdfPath}`);

  // Step 1 — Load PDF
  console.log("\n[1/4] Loading PDF...");
  const pdfInfo = await loadPdf(pdfPath);
  console.log(`       Pages    : ${pdfInfo.numPages}`);
  console.log(`       PDF Type : ${pdfInfo.isDigital ? "Digital (text-based)" : "Scanned (image-based)"}`);

  // Step 2 — Extract text
  console.log("\n[2/4] Extracting text...");
  const rawText = await extractText(pdfInfo);

  if (showRaw) {
    console.log("\n--- RAW EXTRACTED TEXT ---");
    console.log(rawText);
    console.log("--------------------------\n");
  }

  // Step 3 — Parse fields
  console.log("\n[3/4] Parsing Eway Bill fields...");
  const parsed = parseEwayBill(rawText);

  // Step 4 — Save output
  console.log("\n[4/4] Saving output...");
  const jsonPath = saveJson(parsed, OUTPUT_DIR, pdfInfo.filename);
  console.log(`       JSON saved : ${jsonPath}`);

  if (saveCsvFlag) {
    const csvPath = saveCsv(parsed, OUTPUT_DIR, pdfInfo.filename);
    console.log(`       CSV saved  : ${csvPath}`);
  }

  console.log("\n" + "=".repeat(55));
  console.log("  EXTRACTED DATA");
  console.log("=".repeat(55));
  console.log(JSON.stringify(parsed, null, 4));
}

run().catch((err) => {
  console.error("Error:", err.message);
  process.exit(1);
});
