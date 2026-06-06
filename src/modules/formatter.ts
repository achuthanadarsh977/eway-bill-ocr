import fs from "fs";
import path from "path";
import { EwayBillData } from "./parser";

function timestamp(): string {
  return new Date().toISOString().replace(/[:.]/g, "-").slice(0, 19);
}

export function saveJson(data: EwayBillData, outputDir: string, filename: string): string {
  fs.mkdirSync(outputDir, { recursive: true });
  const stem = path.basename(filename, path.extname(filename));
  const outPath = path.join(outputDir, `${stem}_${timestamp()}.json`);
  fs.writeFileSync(outPath, JSON.stringify(data, null, 4), "utf-8");
  return outPath;
}

export function saveCsv(data: EwayBillData, outputDir: string, filename: string): string {
  fs.mkdirSync(outputDir, { recursive: true });
  const stem = path.basename(filename, path.extname(filename));
  const outPath = path.join(outputDir, `${stem}_${timestamp()}.csv`);

  // Flatten nested object into single row
  const flat: Record<string, string> = {};
  for (const [section, fields] of Object.entries(data)) {
    if (typeof fields === "object" && !Array.isArray(fields)) {
      for (const [key, val] of Object.entries(fields)) {
        flat[`${section}__${key}`] = Array.isArray(val) ? val.join("|") : String(val ?? "");
      }
    }
  }

  const headers = Object.keys(flat).join(",");
  const values = Object.values(flat)
    .map((v) => `"${v.replace(/"/g, '""')}"`)
    .join(",");

  fs.writeFileSync(outPath, `${headers}\n${values}\n`, "utf-8");
  return outPath;
}
