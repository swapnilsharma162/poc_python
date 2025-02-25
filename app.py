import os
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import pytesseract
import numpy as np
import pandas as pd
from pdf2image import convert_from_path

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Function to process an image and extract table data
def process_image(image):
    try:
        gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
        text = pytesseract.image_to_string(gray)
        rows = text.split("\n")
        return [row.split() for row in rows if row.strip()]
    except Exception as e:
        logging.error(f"Error processing image: {str(e)}")
        return []

@app.route("/upload", methods=["POST"])
def upload_file():
    try:
        if "file" not in request.files:
            logging.warning("No file part in request")
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files["file"]
        if file.filename == "":
            logging.warning("No file selected")
            return jsonify({"error": "No file selected"}), 400
        
        file_ext = file.filename.rsplit(".", 1)[-1].lower()
        extracted_data = []
        
        if file_ext in ["jpg", "jpeg", "png"]:
            image = cv2.imdecode(np.frombuffer(file.read(), np.uint8), cv2.IMREAD_COLOR)
            extracted_data = process_image(image)
        elif file_ext == "pdf":
            images = convert_from_path(file)
            for img in images:
                extracted_data.extend(process_image(img))
        else:
            logging.warning(f"Unsupported file type: {file_ext}")
            return jsonify({"error": "Unsupported file type"}), 400
        
        df = pd.DataFrame(extracted_data)
        return jsonify({"table_data": df.values.tolist()}), 200
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), 500

@app.errorhandler(500)
def handle_500(error):
    logging.error(f"Server error: {str(error)}")
    return jsonify({"error": "Internal Server Error"}), 500

@app.errorhandler(404)
def handle_404(error):
    logging.warning("Endpoint not found")
    return jsonify({"error": "Not Found"}), 404

@app.errorhandler(400)
def handle_400(error):
    logging.warning("Bad Request")
    return jsonify({"error": "Bad Request"}), 400

if __name__ == "__main__":
    app.run(debug=True)
