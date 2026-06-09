import json
import csv
from pathlib import Path
from datetime import datetime


def to_json(parsed_data: dict, output_dir: str, filename: str) -> str:
    """Save parsed data as a JSON file and return the output path."""
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    stem = Path(filename).stem
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = str(Path(output_dir) / f"{stem}_{timestamp}.json")

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(parsed_data, f, indent=4, ensure_ascii=False)

    return out_path


def to_csv(parsed_data: dict, output_dir: str, filename: str) -> str:
    """Flatten parsed data into a single-row CSV and return the output path."""
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    stem = Path(filename).stem
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = str(Path(output_dir) / f"{stem}_{timestamp}.csv")

    flat = {}
    for section, fields in parsed_data.items():
        if isinstance(fields, dict):
            for key, val in fields.items():
                flat[f"{section}__{key}"] = val if not isinstance(val, list) else "|".join(val)
        else:
            flat[section] = fields

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=flat.keys())
        writer.writeheader()
        writer.writerow(flat)

    return out_path
