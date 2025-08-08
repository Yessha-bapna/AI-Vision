from flask import Flask, request, jsonify
from pdf_parser import extract_faces_from_pdf, extract_faces_from_image
from face_utils import recognize_and_track
import threading
import os

app = Flask(__name__)

@app.route('/upload_file', methods=['POST'])
def upload_file():
    file = request.files['file']
    filename = file.filename.lower()

    if filename.endswith('.pdf'):
        file.save("known_faces.pdf")
        extract_faces_from_pdf("known_faces.pdf")
        return jsonify({"status": "success", "message": "PDF processed"})

    elif filename.endswith(('.jpg', '.jpeg', '.png')):
        path = os.path.join("known_faces", filename)
        os.makedirs("known_faces", exist_ok=True)
        file.save(path)
        extract_faces_from_image(path)
        return jsonify({"status": "success", "message": "Image processed"})

    return jsonify({"status": "fail", "message": "Unsupported file format"})


@app.route('/start_feed')
def start_feed():
    thread = threading.Thread(target=recognize_and_track)
    thread.start()
    return jsonify({"status": "started", "message": "CCTV tracking started"})

if __name__ == "__main__":
    app.run(debug=True)
