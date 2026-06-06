export interface EwayBillData {
  ewb_details: {
    ewb_number: string;
    ewb_date: string;
    valid_until: string;
    supply_type: string;
    transaction_type: string;
    document_number: string;
    document_date: string;
    document_type: string;
    value_of_goods: string;
    reason_for_transport: string;
    irn: string;
  };
  from_party: {
    gstin: string;
    name: string;
    place: string;
    state: string;
    pincode: string;
  };
  to_party: {
    gstin: string;
    name: string;
    place: string;
    state: string;
    pincode: string;
  };
  item_details: {
    hsn_codes: string[];
    products: string[];
    taxable_value: string;
    cgst_rate: string;
    sgst_rate: string;
    igst_rate: string;
    total_value: string;
  };
  transporter_details: {
    transporter_id: string;
    transporter_name: string;
    vehicle_number: string;
    transport_mode: string;
    transport_doc_no: string;
  };
}

function find(pattern: RegExp, text: string): string {
  const match = text.match(pattern);
  return match ? match[1].trim() : "";
}

function cleanGstin(raw: string): string {
  return raw.replace(/\s+/g, "");
}

function cleanEwbNo(raw: string): string {
  return raw.replace(/\s+/g, "");
}

function cleanOcrSpaces(s: string): string {
  let r = s;
  r = r.replace(/(\d) (\d)/g, "$1$2").replace(/(\d) (\d)/g, "$1$2");
  r = r.replace(/\b([A-Z]) ([a-z])/g, "$1$2");
  r = r.replace(/\b([A-Z]{2,3}) ([A-Z]) ([A-Z]{2,})\b/g, "$1$2 $3");
  r = r.replace(/\b([A-Z]) ([A-Z]{3,})\b/g, "$1$2");
  r = r.replace(/\b([A-Z]{2}) ([A-Z]{5,})\b/g, "$1$2");
  r = r.replace(/(\w) -(\w)/g, "$1-$2");
  return r;
}

const KNOWN_SPLITS: [RegExp, string][] = [
  [/\bDeliv\s+ery\b/gi,        "Delivery"],
  [/\bTranspor\s+tation\b/gi,  "Transportation"],
  [/\bTranspor\s+ter\b/gi,     "Transporter"],
  [/\bGener\s+ated\b/gi,       "Generated"],
  [/\bF\s+rom\b/gi,            "From"],
  [/\bdiscr\s+epancy\b/gi,     "discrepancy"],
  [/\bCOIMBA TORE\b/gi,        "COIMBATORE"],
  [/\bKEERANA THAM\b/gi,       "KEERANATHAM"],
  [/\bCHENNA I\b/gi,           "CHENNAI"],
  [/\bBANGA LORE\b/gi,         "BANGALORE"],
  [/\bHYDERA BAD\b/gi,         "HYDERABAD"],
  [/\bAHMEDA BAD\b/gi,         "AHMEDABAD"],
  [/\bBHOPA L\b/gi,            "BHOPAL"],
  [/\bLUCKN OW\b/gi,           "LUCKNOW"],
  [/\bNAGP UR\b/gi,            "NAGPUR"],
  [/\bINDO RE\b/gi,            "INDORE"],
  [/\bVADO DARA\b/gi,          "VADODARA"],
  [/\bSURA T\b/gi,             "SURAT"],
  [/\bKANP UR\b/gi,            "KANPUR"],
  [/\bNASH IK\b/gi,            "NASHIK"],
  [/\bFARIDA BAD\b/gi,         "FARIDABAD"],
  [/\bGAZIABA D\b/gi,          "GHAZIABAD"],
  [/\bRAJKO T\b/gi,            "RAJKOT"],
  [/\bJAIP UR\b/gi,            "JAIPUR"],
  [/\bLUDHIA NA\b/gi,          "LUDHIANA"],
  [/\bAGR A\b/gi,              "AGRA"],
  [/\bMYSU RU\b/gi,            "MYSURU"],
  [/\bKOZHIK ODE\b/gi,         "KOZHIKODE"],
  [/\bTIRUP PUR\b/gi,          "TIRUPPUR"],
  [/\bTIRUNELV ELI\b/gi,       "TIRUNELVELI"],
  [/\bVELLO RE\b/gi,           "VELLORE"],
  [/\bERO DE\b/gi,             "ERODE"],
  [/\bSALE M\b/gi,             "SALEM"],
];

function applyKnownSplits(text: string): string {
  let r = text;
  for (const [pattern, replacement] of KNOWN_SPLITS) {
    r = r.replace(pattern, replacement);
  }
  return r;
}

function parsePlaceLine(line: string): { place: string; state: string; pincode: string } {
  // Apply OCR space fixes before parsing so "T AMIL NADU-6391 18" becomes "TAMIL NADU-639118"
  const cleaned = cleanOcrSpaces(line.trim());
  const m = cleaned.match(/^(.+?),([A-Z][A-Z ]+)-(\d[\d ]{3,5}\d)/);
  if (m) {
    return {
      place:   m[1].trim(),
      state:   m[2].trim(),
      pincode: m[3].replace(/\s+/g, ""),
    };
  }
  return { place: cleaned, state: "", pincode: "" };
}

export function parseEwayBill(text: string): EwayBillData {
  const t = applyKnownSplits(text.replace(/\s+/g, " ").trim());

  // ── EWB header ────────────────────────────────────────────────────────────
  const ewbNoRaw   = find(/E-?Way\s*Bill\s*No[:\s]+([0-9][\s0-9]{10,14}[0-9])/i, t);
  const ewbDate    = find(/E-?Way\s*Bill\s*Date[:\s]+([0-9]{2}\/[0-9]{2}\/[0-9]{4}(?:\s+\d{1,2}:\d{2}\s*[APM]{2})?)/i, t);
  const validUntil = find(/Valid\s*(?:Until|Till|Upto)[:\s]+([0-9]{2}\/[0-9]{2}\/[0-9]{4}(?:\s+\d{1,2}:\d{2}\s*[APM]{2})?)/i, t);
  const supplyType = find(/Supply\s*Type[:\s]+([A-Za-z ]+?)(?=\s+\w)/i, t);
  const transType  = find(/Transaction\s*Type[:\s]+([A-Za-z]+)/i, t);
  const docNo      = find(/Document\s*No\.?\s+([A-Z0-9/\-]+)/i, t);
  const docDate    = find(/Document\s*Date\s+([0-9]{2}\/[0-9]{2}\/[0-9]{4})/i, t);
  const docType    = find(/Document\s*Type[:\s]+([A-Za-z ]+?)(?=\s+\w)/i, t);
  const valueGoods = find(/Value\s*of\s*Goods\s+([0-9,]+(?:\.[0-9]{2})?)/i, t);
  const reason     = find(/Reason\s*for\s*Transportation\s+(.+?)(?=Transporter)/i, t);
  const irn        = find(/IRN[:\s]+([a-f0-9]{64})/i, t);

  // ── From party ────────────────────────────────────────────────────────────
  const fromGstinRaw = find(/GSTIN\s*of\s*Supplier\s+([A-Z0-9 ]+),/i, t);
  const fromName     = find(/GSTIN\s*of\s*Supplier\s+[A-Z0-9 ]+,(.+?)(?=Place\s*of\s*Dispatch)/i, t);
  const dispatchRaw  = find(/Place\s*of\s*Dispatch\s+(.+?)(?=GSTIN\s*of\s*Recipient)/i, t);
  const fromParsed   = parsePlaceLine(dispatchRaw);

  // ── To party ──────────────────────────────────────────────────────────────
  const toGstinRaw  = find(/GSTIN\s*of\s*Recipient\s+([A-Z0-9 ]+)\s*,/i, t);
  const toName      = find(/GSTIN\s*of\s*Recipient\s+[A-Z0-9 ]+\s*,(.+?)(?=Place\s*of\s*Delivery)/i, t);
  const deliveryRaw = find(/Place\s*of\s*Delivery\s+(.+?)(?=Document\s*No)/i, t);
  const toParsed    = parsePlaceLine(deliveryRaw);

  // ── Item details ──────────────────────────────────────────────────────────
  const hsnCode   = find(/HSN\s*Code\s+(\d{4,8})/i, t);
  const product   = find(/HSN\s*Code\s+\d{4,8}\s*-\s*(.+?)(?=Reason)/i, t);

  // ── Transporter ───────────────────────────────────────────────────────────
  const transIdRaw  = find(/Transporter\s+([A-Z0-9 ]+)\s*&/i, t);
  const transName   = find(/Transporter\s+[A-Z0-9 ]+\s*&\s*(.+?)(?=Part\s*-\s*B)/i, t);

  // ── Part B: vehicle and mode ───────────────────────────────────────────────
  const partB        = find(/Part\s*-\s*B\s+(.+)/i, t);
  const modeMatch    = partB.match(/\b(Road|Rail|Air|Ship)\b/i);
  const vehicleMatch = partB.match(/\b([A-Z]{2}\d{1,2}[A-Z]{1,2}\d{4})\b/);

  return {
    ewb_details: {
      ewb_number:           cleanEwbNo(ewbNoRaw),
      ewb_date:             ewbDate,
      valid_until:          validUntil,
      supply_type:          supplyType,
      transaction_type:     transType,
      document_number:      docNo,
      document_date:        docDate,
      document_type:        docType,
      value_of_goods:       valueGoods,
      reason_for_transport: cleanOcrSpaces(reason.trim()),
      irn:                  irn,
    },
    from_party: {
      gstin:   cleanGstin(fromGstinRaw),
      name:    cleanOcrSpaces(fromName.trim()),
      place:   fromParsed.place,
      state:   fromParsed.state,
      pincode: fromParsed.pincode,
    },
    to_party: {
      gstin:   cleanGstin(toGstinRaw),
      name:    cleanOcrSpaces(toName.trim()),
      place:   cleanOcrSpaces(toParsed.place),
      state:   toParsed.state,
      pincode: toParsed.pincode,
    },
    item_details: {
      hsn_codes:     hsnCode ? [hsnCode] : [],
      products:      product ? [cleanOcrSpaces(product.trim())] : [],
      taxable_value: "",
      cgst_rate:     "",
      sgst_rate:     "",
      igst_rate:     "",
      total_value:   valueGoods,
    },
    transporter_details: {
      transporter_id:   cleanGstin(transIdRaw),
      transporter_name: cleanOcrSpaces(transName.trim()),
      vehicle_number:   vehicleMatch ? vehicleMatch[1] : "",
      transport_mode:   modeMatch   ? modeMatch[1]   : "",
      transport_doc_no: "",
    },
  };
}
