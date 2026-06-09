import os
import json
from flask import Flask, request, jsonify, render_template, send_file
from werkzeug.utils import secure_filename
from flask_cors import CORS
from modules.pdf_loader import load_pdf, load_image, IMAGE_EXTENSIONS
from modules.ocr_engine import extract_text
from modules.parser import parse_eway_bill
from modules.formatter import to_json

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "output"
PDF_EXTENSIONS = {"pdf"}
ALLOWED_EXTENSIONS = PDF_EXTENSIONS | {ext.lstrip(".") for ext in IMAGE_EXTENSIONS}

app = Flask(__name__)
CORS(app)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 32 * 1024 * 1024  # 32 MB max (images can be large)

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def is_image_file(filename):
    ext = "." + filename.rsplit(".", 1)[1].lower()
    return ext in IMAGE_EXTENSIONS


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    # Accept field name "pdf" or "file" for backwards compatibility
    file = request.files.get("pdf") or request.files.get("file")
    if file is None:
        return jsonify({"error": "No file provided"}), 400

    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": f"Allowed types: PDF, {', '.join(sorted(IMAGE_EXTENSIONS))}"}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)

    try:
        if is_image_file(filename):
            file_info = load_image(file_path)
            file_type = "Scanned Image"
        else:
            file_info = load_pdf(file_path)
            file_type = "Digital PDF" if file_info["is_digital"] else "Scanned PDF"

        raw_text  = extract_text(file_info)
        parsed    = parse_eway_bill(raw_text)
        json_path = to_json(parsed, OUTPUT_FOLDER, filename)

        return jsonify({
            "success": True,
            "filename": filename,
            "pages": file_info["num_pages"],
            "pdf_type": file_type,
            "json_file": os.path.basename(json_path),
            "data": parsed,
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if os.path.exists(file_path):
            os.remove(file_path)


@app.route("/download/<filename>")
def download(filename):
    filepath = os.path.join(OUTPUT_FOLDER, secure_filename(filename))
    if not os.path.exists(filepath):
        return jsonify({"error": "File not found"}), 404
    return send_file(filepath, as_attachment=True)


if __name__ == "__main__":
    import waitress
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting server on port {port}...")
    waitress.serve(app, host="0.0.0.0", port=port)
