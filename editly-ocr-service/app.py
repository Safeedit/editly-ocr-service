from flask import Flask, request, jsonify
from pdf2image import convert_from_path
import pytesseract
import os
import tempfile

app = Flask(__name__)

@app.route("/ocr", methods=["POST"])
def ocr_pdf():
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    with tempfile.TemporaryDirectory() as tmpdir:
        pdf_path = os.path.join(tmpdir, "temp.pdf")
        file.save(pdf_path)
        pages = convert_from_path(pdf_path)
        
        full_text = ""
        for page in pages:
            full_text += pytesseract.image_to_string(page) + "\n"

        return jsonify({"text": full_text})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
