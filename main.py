import cv2
import face_recognition
import mediapipe as mp
import os
from datetime import datetime

from detector import YOLODetector

# Initialize detector
detector = YOLODetector()

# MediaPipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True
)

# Load known face
known_image = face_recognition.load_image_file("known_face.jpg")
known_encoding = face_recognition.face_encodings(known_image)[0]

# Webcam
cap = cv2.VideoCapture(0)

# Stable person detection
stable_person_count = 0
person_frames = 0

# Create screenshot folder
if not os.path.exists("screenshots"):
    os.makedirs("screenshots")

while True:

    success, frame = cap.read()

    if not success:
        break

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    detections = detector.detect_objects(frame)

    current_person_count = 0
    mobile_detected = False

    # YOLO detections
    for detection in detections:

        label = detection["label"]
        confidence = detection["confidence"]
        x, y, w, h = detection["box"]

        # Real person detection only
        if label == "person" and confidence > 0.4:

            if w > 120 and h > 120:
                current_person_count += 1

        # Mobile detection
        if label == "cell phone" and confidence > 0.4:
            mobile_detected = True

        # Draw boxes
        cv2.rectangle(
            frame,
            (x, y),
            (x + w, y + h),
            (0, 255, 0),
            2
        )

        cv2.putText(
            frame,
            f"{label} {confidence:.2f}",
            (x, y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
             (0, 255, 0),
            2
        )

    # Stable detection logic
    if current_person_count >= 2:

        stable_person_count = 2
        person_frames = 20

    elif person_frames > 0:

        person_frames -= 1

    else:

        stable_person_count = current_person_count

    # Face Recognition
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(
        rgb_frame,
        face_locations
    )

    authorized = False
    for face_encoding in face_encodings:

        matches = face_recognition.compare_faces(
            [known_encoding],
            face_encoding
        )

        if True in matches:
            authorized = True

    if authorized:

        cv2.putText(
            frame,
            "Authorized Student",
            (20, 170),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2
        )

    else:

        cv2.putText(
            frame,
            "Unauthorized Person!",
            (20, 170),
            cv2.FONT_HERSHEY_SIMPLEX,
             0.8,
            (0, 0, 255),
            2
        )

    # Looking Away Detection
    results = face_mesh.process(rgb_frame)

    if results.multi_face_landmarks:

        for face_landmarks in results.multi_face_landmarks:

            nose = face_landmarks.landmark[1]

            nose_x = int(nose.x * frame.shape[1])

            if nose_x < 220:

                cv2.putText(
                    frame,
                    "Looking Left",
                    (20, 210),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 0, 255),
                    2
                )

            elif nose_x >420:

                cv2.putText(
                    frame,
                    "Looking Right",
                    (20, 210),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 0, 255),
                    2
                )

            else:

                cv2.putText(
                    frame,
                    "Looking Forward",
                    (20, 210),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 255, 0),
                    2
                )

    # Person count
    cv2.putText(
         frame,
        f"Persons Detected: {stable_person_count}",
        (20, 50),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 0, 0),
        2
    )

    suspicious = False

    # Multiple person warning
    if stable_person_count >= 2:

        suspicious = True

        cv2.putText(
            frame,
            "WARNING: Multiple Persons Detected!",
            (20, 90),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 0, 255),
            2
        )

    # Mobile warning
    if mobile_detected:

        suspicious = True

        cv2.putText(
            frame,
            "WARNING: Mobile Phone Detected!",
            (20, 130),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 0, 255),
            2
        )

    # Screenshot Capture
    if suspicious:

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        filename = f"screenshots/cheating_{timestamp}.png"

        cv2.imwrite(filename, frame)

    # Show output
    cv2.imshow("AI Exam Proctoring System", frame)

    # Exit
    key = cv2.waitKey(1)

    if key == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()

