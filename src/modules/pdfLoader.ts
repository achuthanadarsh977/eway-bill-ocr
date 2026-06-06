import fs from "fs";
import path from "path";
import pdfParse from "pdf-parse";

export interface PdfInfo {
  path: string;
  filename: string;
  numPages: number;
  isDigital: boolean;
  rawBuffer: Buffer;
  pagesText: string[];
}

export async function loadPdf(pdfPath: string): Promise<PdfInfo> {
  if (!fs.existsSync(pdfPath)) {
    throw new Error(`PDF not found: ${pdfPath}`);
  }

  const buffer = fs.readFileSync(pdfPath);
  const pagesText: string[] = [];

  const data = await pdfParse(buffer, {
    pagerender: (pageData: any) => {
      return pageData.getTextContent().then((content: any) => {
        const text = content.items.map((item: any) => item.str).join(" ");
        pagesText.push(text.trim());
        return text;
      });
    },
  });

  const totalText = pagesText.join(" ").trim();
  const isDigital = totalText.length > 50;

  return {
    path: pdfPath,
    filename: path.basename(pdfPath),
    numPages: data.numpages,
    isDigital,
    rawBuffer: buffer,
    pagesText,
  };
}
