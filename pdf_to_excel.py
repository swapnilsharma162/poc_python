from flask import Flask, request, jsonify
import cv2
import pytesseract
import numpy as np
import pandas as pd
from flask_cors import CORS
from pdf2image import convert_from_bytes

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Ensure Tesseract is installed and its path is correctly set
pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

def extract_table_from_image(image):
    """Extract table data from an image using OpenCV and Tesseract OCR."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    extracted_text = []
    
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if w > 50 and h > 10:
            roi = gray[y:y+h, x:x+w]
            text = pytesseract.image_to_string(roi, config='--psm 6')
            extracted_text.append(text.strip())
    
    return extracted_text

@app.route("/upload", methods=["POST"])
def upload():
    """Handle image or PDF upload and return extracted table data."""
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files["file"]
    filename = file.filename.lower()
    extracted_data = []
    
    if filename.endswith(".pdf"):
        images = convert_from_bytes(file.read())
        for image in images:
            image_np = np.array(image)
            extracted_data.extend(extract_table_from_image(image_np))
    else:
        image = np.frombuffer(file.read(), np.uint8)
        image = cv2.imdecode(image, cv2.IMREAD_COLOR)
        extracted_data = extract_table_from_image(image)
    
    return jsonify({"table_data": extracted_data})

if __name__ == "__main__":
    app.run(debug=True)
