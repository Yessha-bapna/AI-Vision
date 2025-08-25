from flask import Flask, request, jsonify
from pdf_parser import extract_faces_from_pdf, extract_faces_from_image
from face_utils import recognize_and_track, LIVE_LOGS
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


@app.route("/start_feed", methods=["GET"])
def start_feed():
    def run_camera():
        recognize_and_track(0)   # <- opens OpenCV window

    t = threading.Thread(target=run_camera, daemon=True)
    t.start()
    return jsonify({"message": "🚨 CCTV feed started (check your camera window)"})

@app.route("/get_logs", methods=["GET"])
def get_logs():
    return jsonify(LIVE_LOGS)

if __name__ == "__main__":
    app.run(debug=True)
