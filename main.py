import cv2
import face_recognition
import os

# Load known faces
print("Loading known faces...")
known_encodings = []
known_names = []

known_dir = 'known_faces'  # Folder name

for filename in os.listdir(known_dir):
    if filename.endswith(('.jpg', '.jpeg', '.png')):
        path = os.path.join(known_dir, filename)
        image = face_recognition.load_image_file(path)
        encodings = face_recognition.face_encodings(image)

        if encodings:
            known_encodings.append(encodings[0])
            name = os.path.splitext(filename)[0]
            known_names.append(name)
            print(f"Loaded face for: {name}")
        else:
            print(f"Warning: No face found in {filename}")

# Start webcam
print("Starting camera...")
video_capture = cv2.VideoCapture(0)

# Optional: stricter tolerance
TOLERANCE = 0.45

while True:
    ret, frame = video_capture.read()
    if not ret:
        print("Failed to grab frame.")
        break

    # Resize and convert color
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

    # Detect faces
    face_locations = face_recognition.face_locations(rgb_small_frame)
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        matches = face_recognition.compare_faces(known_encodings, face_encoding, tolerance=TOLERANCE)
        name = "Access Denied"

        face_distances = face_recognition.face_distance(known_encodings, face_encoding)
        if matches:
            best_match_index = face_distances.argmin()
            if matches[best_match_index]:
                name = f"Access Granted: {known_names[best_match_index]}"

        # Scale back up face locations
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        # Draw box
        color = (0, 255, 0) if "Granted" in name else (0, 0, 255)
        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
        cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

    cv2.imshow('Face Unlock System', frame)

    # Press 'q' to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
video_capture.release()
cv2.destroyAllWindows()
