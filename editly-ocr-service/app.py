from flask import Flask, request, jsonify
from flask_cors import CORS
from pdf2image import convert_from_path
from PIL import Image
import pytesseract
import os
import tempfile

app = Flask(__name__)
CORS(app)  # ✅ Enable CORS

@app.route("/ocr", methods=["POST"])
def ocr_file():
    file = request.files.get("file")
    lang = request.form.get("lang", "eng")  # ✅ Default to English
    max_pages = int(request.form.get("max_pages", 5))  # ✅ Limit pages to avoid crash

    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    filename = file.filename.lower()

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = os.path.join(tmpdir, filename)
            file.save(input_path)

            full_text = ""

            # ✅ Handle image OCR (JPG/PNG)
            if filename.endswith((".jpg", ".jpeg", ".png")):
                image = Image.open(input_path)
                full_text = pytesseract.image_to_string(image, lang=lang)

            # ✅ Handle PDF OCR
            elif filename.endswith(".pdf"):
                pages = convert_from_path(input_path, dpi=200)

                if len(pages) > max_pages:
                    pages = pages[:max_pages]  # Limit number of pages

                for i, page in enumerate(pages):
                    text = pytesseract.image_to_string(page, lang=lang)
                    full_text += f"\n\n--- Page {i+1} ---\n{text}"

            else:
                return jsonify({"error": "Unsupported file type"}), 400

            return jsonify({"text": full_text})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
