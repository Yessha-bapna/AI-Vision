
import cv2
import face_recognition
import os
import csv
from datetime import datetime
import mediapipe as mp

# MediaPipe Pose setup
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=False, model_complexity=1, enable_segmentation=False, min_detection_confidence=0.5)

# Load known criminal face encodings
def load_known_faces(directory='known_faces'):
    encodings = []
    names = []
    for filename in os.listdir(directory):
        if filename.endswith(('.jpg', '.jpeg', '.png')):
            path = os.path.join(directory, filename)
            image = face_recognition.load_image_file(path)
            encoding = face_recognition.face_encodings(image)
            if encoding:
                encodings.append(encoding[0])
                names.append(os.path.splitext(filename)[0])
    return encodings, names

# Detect simple activities using pose landmarks

def detect_activity(landmarks):
    def is_visible(landmark):
        return landmark.visibility > 0.7

    try:
        left_wrist = landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value]
        right_wrist = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value]
        left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
        right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
        left_ear = landmarks[mp_pose.PoseLandmark.LEFT_EAR.value]
        right_ear = landmarks[mp_pose.PoseLandmark.RIGHT_EAR.value]
        nose = landmarks[mp_pose.PoseLandmark.NOSE.value]
        left_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
        right_hip = landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value]

        avg_hip_y = (left_hip.y + right_hip.y) / 2
        relaxed_threshold = avg_hip_y + 0.1
        shoulder_y = (left_shoulder.y + right_shoulder.y) / 2

        # Detect Raising hand
        if is_visible(left_wrist) and left_wrist.y < shoulder_y - 0.05:
            return "Raising hand (Left)"
        elif is_visible(right_wrist) and right_wrist.y < shoulder_y - 0.05:
            return "Raising hand (Right)"

        # Detect Talking on Phone (wrist near ear region)
        if (
            is_visible(left_wrist) and is_visible(left_ear) and abs(left_wrist.y - left_ear.y) < 0.08 and abs(left_wrist.x - left_ear.x) < 0.08
        ) or (
            is_visible(right_wrist) and is_visible(right_ear) and abs(right_wrist.y - right_ear.y) < 0.08 and abs(right_wrist.x - right_ear.x) < 0.08
        ):
            return "Talking on phone"

        # Detect Idle arms down
        if (
            is_visible(left_wrist) and is_visible(right_wrist) and
            left_wrist.y > relaxed_threshold and right_wrist.y > relaxed_threshold
        ):
            return "Idle"

        return "Idle"
    except:
        return "Unknown"

def log_activity(name, activity):
    log_file = "activity_logs.csv"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    row = [timestamp, name, activity]

    file_exists = os.path.exists(log_file)
    with open(log_file, mode='a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Timestamp", "Name", "Activity"])
        writer.writerow(row)

# Main function to track faces and activities
def recognize_and_track():
    print("🔄 Loading known faces...")
    known_encodings, known_names = load_known_faces()

    video = cv2.VideoCapture(0)
    video.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    video.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    if not video.isOpened():
        print("❌ Could not open webcam.")
        return

    print("📹 Starting real-time face and activity tracking...")

    while True:
        ret, frame = video.read()
        if not ret or frame is None:
            print("⚠️ Empty frame — exiting.")
            break

        resized = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        rgb_small = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_small)
        face_encodings = face_recognition.face_encodings(rgb_small, face_locations)

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(rgb_frame)
        activity = "Idle"
        if results.pose_landmarks:
            activity = detect_activity(results.pose_landmarks.landmark)

        for (top, right, bottom, left), encoding in zip(face_locations, face_encodings):
            name = "Unknown"
            label = "CLEAR"

            matches = face_recognition.compare_faces(known_encodings, encoding, tolerance=0.45)
            face_distances = face_recognition.face_distance(known_encodings, encoding)

            if matches:
                best_match_index = face_distances.argmin()
                if matches[best_match_index]:
                    raw_name = known_names[best_match_index].replace("_", " ")
                    name = raw_name
                    label = f"CRIMINAL - {name}"

            top *= 2
            right *= 2
            bottom *= 2
            left *= 2

            color = (0, 0, 255) if "CRIMINAL" in label else (0, 255, 0)

            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.putText(frame, f"{label} - {activity}", (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

            log_activity(name, activity)

        cv2.imshow("🚨 Railway Criminal Tracker", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video.release()
    cv2.destroyAllWindows()
