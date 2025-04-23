# face_emotion.py

import cv2
import mediapipe as mp
from deepface import DeepFace
import numpy as np
import threading
import time

# Globals
last_emotion = "Undetected"
running = True

# Face detection setup
mp_face_detection = mp.solutions.face_detection
detector = mp_face_detection.FaceDetection(model_selection=0, min_detection_confidence=0.7)

def enhance_contrast(image):
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    cl = clahe.apply(l)
    enhanced = cv2.merge((cl, a, b))
    return cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)

def emotion_loop():
    global last_emotion, running
    cap = cv2.VideoCapture(0)

    while running:
        ret, frame = cap.read()
        if not ret:
            continue

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = detector.process(rgb_frame)

        if results.detections:
            for detection in results.detections:
                ih, iw, _ = frame.shape
                bbox = detection.location_data.relative_bounding_box
                x, y, w, h = int(bbox.xmin * iw), int(bbox.ymin * ih), int(bbox.width * iw), int(bbox.height * ih)
                margin = 20
                x1, y1 = max(0, x - margin), max(0, y - margin)
                x2, y2 = min(iw, x + w + margin), min(ih, y + h + margin)
                face_crop = enhance_contrast(frame[y1:y2, x1:x2])

                try:
                    result = DeepFace.analyze(face_crop, actions=['emotion'], enforce_detection=False)
                    last_emotion = result[0]['dominant_emotion']
                except:
                    last_emotion = "Undetected"

                # Draw + label
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, f'Emotion: {last_emotion}', (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
        else:
            cv2.putText(frame, "No face detected", (30, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        cv2.imshow("Face Emotion", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            running = False

    cap.release()
    cv2.destroyAllWindows()

def start_emotion_detection():
    thread = threading.Thread(target=emotion_loop)
    thread.start()

def get_last_emotion():
    return last_emotion

if __name__ == '__main__':
    start_emotion_detection()
    try:
        while True:
            time.sleep(1)
            print(f"Last detected emotion: {get_last_emotion()}")
    except KeyboardInterrupt:
        print("Stopping face emotion detection...")
        running = False
