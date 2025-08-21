# file: face_utils.py
import os
import cv2
import csv
import math
import face_recognition
from datetime import datetime, timedelta
import mediapipe as mp
import numpy as np

# -----------------------------
# Config
# -----------------------------
KNOWN_DIR = "known_faces"
LOG_PATH = "activity_logs.csv"
FACE_MODEL = "hog"   # "hog" for CPU; use "cnn" if you have CUDA build
TOLERANCE = 0.45     # match strictness
RESIZE_RATIO = 0.5   # speed-up factor (0.5 = process at half-res)

# Cooldown for group alerts (seconds)
GROUP_ALERT_COOLDOWN = 10
_last_group_alert_time = None

# -----------------------------
# Setup: MediaPipe Pose (single-person)
# We'll run it once per person on a cropped ROI -> multi-person overall
# -----------------------------
mp_pose = mp.solutions.pose
_pose = mp_pose.Pose(
    static_image_mode=False,
    model_complexity=1,
    enable_segmentation=False,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5,
)

# -----------------------------
# Known gallery
# -----------------------------
def load_known_faces(directory=KNOWN_DIR):
    encodings, names = [], []
    if not os.path.isdir(directory):
        os.makedirs(directory, exist_ok=True)
        return encodings, names

    for fn in os.listdir(directory):
        if not fn.lower().endswith((".png", ".jpg", ".jpeg")):
            continue
        path = os.path.join(directory, fn)
        img = face_recognition.load_image_file(path)
        encs = face_recognition.face_encodings(img)
        if not encs:
            continue
        encodings.append(encs[0])
        # label from filename (no extension)
        names.append(os.path.splitext(fn)[0])
    return encodings, names

KNOWN_ENCODINGS, KNOWN_NAMES = load_known_faces()

# -----------------------------
# Logging
# -----------------------------
def log_activity(identity, activity, is_criminal):
    newfile = not os.path.exists(LOG_PATH)
    with open(LOG_PATH, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if newfile:
            w.writerow(["timestamp", "identity", "role", "activity"])
        role = "CRIMINAL" if is_criminal else "CIVILIAN"
        w.writerow([datetime.now().isoformat(), identity, role, activity])

# -----------------------------
# Activity heuristics (pose)
# -----------------------------
def _dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])

def _landmark_xy(landmarks, idx, w, h):
    lm = landmarks[idx]
    return (lm.x * w, lm.y * h)

def infer_activity_for_face_roi(bgr_roi):
    rgb = cv2.cvtColor(bgr_roi, cv2.COLOR_BGR2RGB)
    res = _pose.process(rgb)
    if not res.pose_landmarks:
        return "Idle"

    h, w = bgr_roi.shape[:2]
    lms = res.pose_landmarks.landmark
    try:
        rw = _landmark_xy(lms, mp_pose.PoseLandmark.RIGHT_WRIST.value, w, h)
        lw = _landmark_xy(lms, mp_pose.PoseLandmark.LEFT_WRIST.value,  w, h)
        rs = _landmark_xy(lms, mp_pose.PoseLandmark.RIGHT_SHOULDER.value, w, h)
        ls = _landmark_xy(lms, mp_pose.PoseLandmark.LEFT_SHOULDER.value,  w, h)
        re = _landmark_xy(lms, mp_pose.PoseLandmark.RIGHT_EAR.value, w, h)
        le = _landmark_xy(lms, mp_pose.PoseLandmark.LEFT_EAR.value,  w, h)
        nose = _landmark_xy(lms, mp_pose.PoseLandmark.NOSE.value, w, h)
    except Exception:
        return "Idle"

    diag = math.hypot(w, h)
    near_thresh = 0.08 * diag

    right_raised = rw[1] < rs[1] - 0.05 * h
    left_raised  = lw[1] < ls[1] - 0.05 * h

    right_phone = _dist(rw, re) < near_thresh
    left_phone  = _dist(lw, le) < near_thresh

    if right_phone or left_phone:
        return "Talking on phone (R)" if right_phone else "Talking on phone (L)"
    if right_raised and left_raised:
        return "Both hands up"
    if right_raised:
        return "Raising right hand"
    if left_raised:
        return "Raising left hand"
    if rw[1] < nose[1] - 0.03 * h or lw[1] < nose[1] - 0.03 * h:
        return "Hand near face"
    return "Idle"

# -----------------------------
# Main loop
# -----------------------------
def recognize_and_track(video_source=0):
    global KNOWN_ENCODINGS, KNOWN_NAMES, _last_group_alert_time

    KNOWN_ENCODINGS, KNOWN_NAMES = load_known_faces()

    cap = cv2.VideoCapture(video_source)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open video source {video_source}")

    while True:
        ok, frame = cap.read()
        if not ok:
            break

        small = cv2.resize(frame, None, fx=RESIZE_RATIO, fy=RESIZE_RATIO, interpolation=cv2.INTER_LINEAR)
        rgb_small = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)

        face_locs_small = face_recognition.face_locations(rgb_small, model=FACE_MODEL)
        face_encs_small = face_recognition.face_encodings(rgb_small, face_locs_small)

        criminal_count = 0

        for (top, right, bottom, left), enc in zip(face_locs_small, face_encs_small):
            top    = int(top    / RESIZE_RATIO)
            right  = int(right  / RESIZE_RATIO)
            bottom = int(bottom / RESIZE_RATIO)
            left   = int(left   / RESIZE_RATIO)

            name = "Unknown"
            is_criminal = False
            if KNOWN_ENCODINGS:
                matches = face_recognition.compare_faces(KNOWN_ENCODINGS, enc, tolerance=TOLERANCE)
                dists = face_recognition.face_distance(KNOWN_ENCODINGS, enc)
                if len(dists) > 0:
                    best_idx = int(np.argmin(dists))
                    if matches[best_idx]:
                        raw = KNOWN_NAMES[best_idx]
                        name = raw.replace("_", " ")
                        is_criminal = True
                        criminal_count += 1

            h, w = frame.shape[:2]
            bw, bh = (right - left), (bottom - top)
            pad_x = int(0.5 * bw)
            pad_y_top = int(0.5 * bh)
            pad_y_bottom = int(2.0 * bh)
            x1 = max(0, left - pad_x)
            y1 = max(0, top - pad_y_top)
            x2 = min(w, right + pad_x)
            y2 = min(h, bottom + pad_y_bottom)
            roi = frame[y1:y2, x1:x2].copy()
            activity = infer_activity_for_face_roi(roi) if roi.size else "Idle"

            color = (0, 0, 255) if is_criminal else (0, 200, 0)
            label = f"{'CRIMINAL' if is_criminal else 'CIVILIAN'} - {name if is_criminal else 'CLEAR'}"
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.putText(frame, f"{label} | {activity}", (left, max(20, top - 8)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2, cv2.LINE_AA)

            ident = name if is_criminal else "Unknown/Civilian"
            log_activity(ident, activity, is_criminal)

        # --------- GROUP ALERT CHECK ----------
        if criminal_count >= 2:
            now = datetime.now()
            if _last_group_alert_time is None or (now - _last_group_alert_time) > timedelta(seconds=GROUP_ALERT_COOLDOWN):
                log_activity("Multiple", f"Group of {criminal_count} criminals detected", True)
                _last_group_alert_time = now

            cv2.putText(frame,
                        f"🚨 ALERT: Criminal Group Detected ({criminal_count})",
                        (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1.2,
                        (0, 0, 255),
                        4,
                        cv2.LINE_AA)

        cv2.imshow("🚨 Railway Criminal Tracker — Multi-Person", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
