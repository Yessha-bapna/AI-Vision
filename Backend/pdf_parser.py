from pdf2image import convert_from_path
import face_recognition
import cv2
import os

def extract_faces_from_pdf(pdf_path, output_dir='known_faces'):
    os.makedirs(output_dir, exist_ok=True)
    pages = convert_from_path(pdf_path)
    count = 0
    for i, page in enumerate(pages):
        image_path = f"page_{i}.jpg"
        page.save(image_path, "JPEG")
        image = face_recognition.load_image_file(image_path)
        face_locations = face_recognition.face_locations(image)
        for j, (top, right, bottom, left) in enumerate(face_locations):
            face = image[top:bottom, left:right]
            name = f"criminal_{count}"
            save_path = os.path.join(output_dir, f"{name}.jpg")
            cv2.imwrite(save_path, cv2.cvtColor(face, cv2.COLOR_RGB2BGR))
            count += 1
        os.remove(image_path)

def extract_faces_from_image(image_path, output_dir='known_faces'):
    os.makedirs(output_dir, exist_ok=True)
    image = face_recognition.load_image_file(image_path)
    face_locations = face_recognition.face_locations(image)
    for j, (top, right, bottom, left) in enumerate(face_locations):
        face = image[top:bottom, left:right]
        name = f"criminal_img_{j}"
        save_path = os.path.join(output_dir, f"{name}.jpg")
        cv2.imwrite(save_path, cv2.cvtColor(face, cv2.COLOR_RGB2BGR))

       
