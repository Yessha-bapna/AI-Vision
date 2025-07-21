
# 🔒 Face Recognition Access Control System

This project uses your webcam and face recognition to grant or deny access. It detects faces in real-time and checks them against known images in a folder. If your face matches, you get **Access Granted**, otherwise **Access Denied** is shown.

---

## 🧠 Features

- Real-time face detection and recognition using webcam.
- Easy to add new known faces by uploading images.
- Grants or denies access based on match confidence.

---

## 🗂️ Folder Structure

```
project/
│
├── known_faces/           # Store reference images here (e.g. John.jpg, Alice.png)
├── face_unlock.py         # Main Python script
├── README.md              # This file
```

---

## ⚙️ Requirements

- Python 3.8+
- OpenCV
- face_recognition (built on dlib)
- dlib (C++ dependency)

---

## 🧩 Python Package Installation

```bash
pip install opencv-python face_recognition
```

---

## 🛠️ Installing CMake and C++ Build Tools (Important for dlib)

> These are required to compile dlib, which is used by `face_recognition`.

### 🔧 Step-by-Step Setup on Windows

#### ✅ 1. Download and Install CMake

- Go to: [https://cmake.org/download/](https://cmake.org/download/)
- Download the **Windows Installer (64-bit)** version.
- During installation, make sure to **check the box that says "Add CMake to system PATH for all users"**.

#### ✅ 2. Download and Install Visual C++ Build Tools

- Go to: [https://visualstudio.microsoft.com/visual-cpp-build-tools/](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
- Download the **Build Tools for Visual Studio**.
- During the installation, check the following workloads:
  - ✅ **C++ build tools**
  - ✅ **Windows 10 SDK**
  - ✅ **C++ CMake tools for Windows**

> These are necessary to compile and run `dlib` and `face_recognition`.

#### 🔁 3. Restart Your Computer

> Restarting helps your system register the new environment variables and tools.

#### 💡 4. Install dlib

After reboot, open your terminal or command prompt and run:

```bash
pip install dlib
```

If everything is set up correctly, it should install without errors.

---

## 🏁 How to Run

1. Place images of known people in the `known_faces` folder.
   - File names will be used as names for recognition (e.g. `Yessha.jpg` → "Yessha").

2. Run the Python script:

```bash
python face_unlock.py
```

3. A webcam window will appear. When your face is detected:
   - ✅ If matched → Green box and `Access Granted: YourName`
   - ❌ If not matched → Red box and `Access Denied`

4. Press `q` to quit.

---

## 🧪 Sample known_faces folder:

```
known_faces/
├── yessha.jpg
├── Jeff.jpeg
```

---

## 🧯 Troubleshooting

| Issue | Solution |
|-------|----------|
| `face_recognition` install fails | Ensure CMake and C++ Build Tools are properly installed |
| No face detected in known image | Use a clearer image with a single face |
| Webcam not detected | Make sure it's connected and not being used by another app |
| `IndexError: list index out of range` | The script tried to encode a face from an image with **no detectable face** |

---

## 🤝 Credits

- Built with `face_recognition` by Adam Geitgey  
- Uses `OpenCV` for real-time video processing  
- Based on `dlib` for deep face encoding  

---

