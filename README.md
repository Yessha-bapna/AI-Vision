# 🚨 Railway Criminal Tracker System

This project is a full-stack face recognition system for tracking criminals using CCTV and document uploads. It consists of a Flask backend for face extraction and tracking, and a Streamlit frontend for user interaction.

---

## 📁 Folder Structure

```
FaceDetectionSystem/
│
├── Backend/
│   ├── app.py                # Flask backend server
│   ├── face_utils.py         # Face recognition and activity tracking logic
│   ├── pdf_parser.py         # PDF/image face extraction utilities
│   ├── known_faces/          # Stores extracted/known face images
│   └── __pycache__/          # Python cache files
│
├── Frontend/
│   ├── app.py                # Streamlit frontend app (UI with live logs + CCTV control)
│   └── requirements.txt      # Frontend dependencies
│
├── README.md                 # This file
├── .gitignore                # Git ignore rules
```

---

## 🖥️ Prerequisites

- Python 3.8+
- Webcam (for CCTV tracking)
- pip (Python package manager)
- CMake & Visual C++ Build Tools (for dlib, see below)

---

## ⚙️ Step 1: Clone the Repository

```bash
git clone https://github.com/Yessha-bapna/AI-Vision
```

---

## 🛠️ Step 2: Create and Activate Virtual Environments

**It is recommended to use separate virtual environments for Backend and Frontend.**

### Backend

```bash
cd Backend
python -m venv venv
venv\Scripts\activate   # On Windows
# Or
source venv/bin/activate  # On Mac/Linux
```

### Frontend

Open a new terminal:

```bash
cd Frontend
python -m venv venv
venv\Scripts\activate   # On Windows
# Or
source venv/bin/activate  # On Mac/Linux
```

---

## 📦 Step 3: Install Dependencies

### Backend

Install required packages:

```bash
pip install flask opencv-python face_recognition pdf2image pytesseract Pillow mediapipe requests numpy
```

> **Note:** You may need to install `dlib` separately.  
> See instructions below if you encounter errors.

### Frontend

Install dependencies from `requirements.txt`:

```bash
pip install -r requirements.txt
```

---

## 🛠️ Step 4: Install CMake and Visual C++ Build Tools (Windows Only)

These are required for `dlib` and `face_recognition`.

1. **CMake:** [Download here](https://cmake.org/download/)  
2. **Visual C++ Build Tools:** [Download here](https://visualstudio.microsoft.com/visual-cpp-build-tools/)  
   - During installation, select:
     - C++ build tools
     - Windows 10 SDK
     - C++ CMake tools for Windows

After installation, restart your computer.

Then install dlib:

```bash
pip install dlib
```

---

## 🖼️ Step 5: Prepare Known Faces

- Place images of criminals or known people in `Backend/known_faces/`.  
- You can also upload PDFs or images via the frontend to auto-extract faces.  
- Faces will be saved automatically into the gallery.

---

## 🚀 Step 6: Run the Backend Server

In the `Backend` folder and with the venv activated:

```bash
python app.py
```

- The Flask server will start at `http://localhost:5000`.

---

## 🌐 Step 7: Run the Frontend App

In the `Frontend` folder and with the venv activated:

```bash
python -m streamlit run app.py
```

- The Streamlit app will open in your browser.  
- The UI is split into **two panels**:
  - **Left side:** Upload section (PDFs/Images + CCTV control)  
  - **Right side:** Live activity logs from CCTV feed  

---

## 📝 How to Use

1. **Upload Criminal PDF or Image:**  
   - Use the Streamlit UI to upload a PDF or image containing faces.  
   - The backend will extract faces and save them in `Backend/known_faces/`.

2. **Start CCTV Tracking:**  
   - Click **"Start CCTV Tracking"** in the frontend.  
   - The backend will start real-time face and activity tracking using your webcam.  
   - Detected **criminals are highlighted in red**, civilians in green.  

3. **Features Added:**  
   - Detects **multiple criminals and civilians** simultaneously.  
   - Gives an **alert when criminals group together** (stand too close).  
   - Detects activities like **raising hand, talking on phone, idle**, etc.  
   - Logs are written to `activity_logs.csv`.  
   - **Live activity logs appear on the dashboard** alongside the CCTV feed.

4. **View Results:**  
   - Webcam window shows bounding boxes with role & activity.  
   - Logs stream live in the Streamlit UI.  
   - Press `q` to quit the webcam window.

---

## 🧯 Troubleshooting

| Issue | Solution |
|-------|----------|
| `face_recognition`/`dlib` install fails | Ensure CMake and Visual C++ Build Tools are installed |
| No face detected in known image | Use a clearer image with a single face |
| Webcam not detected | Make sure it's connected and not used by another app |
| `IndexError: list index out of range` | The image may not contain a detectable face |
| Logs not updating | Ensure backend is running and `/get_logs` endpoint is reachable |

---

## 🤝 Credits

- Built with `face_recognition` by Adam Geitgey  
- Uses `OpenCV` for real-time video processing  
- Based on `dlib` for deep face encoding  
- Activity recognition via **MediaPipe**  
- Frontend powered by **Streamlit**
