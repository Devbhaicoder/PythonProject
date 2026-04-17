import face_recognition
import cv2
import numpy as np
import csv
from datetime import datetime

video_capture = cv2.VideoCapture(0)

# Load images
dev_image = face_recognition.load_image_file("faces/devansh.jpg")
dev_encoding = face_recognition.face_encodings(dev_image)[0]

surya_image = face_recognition.load_image_file("faces/suryansh.jpg")
surya_encoding = face_recognition.face_encodings(surya_image)[0]

known_faces_encodings = [dev_encoding, surya_encoding]
known_faces_names = ["devansh", "suryansh"]

# Students list
students = known_faces_names.copy()

# Create CSV file
now = datetime.now()
current_date = now.strftime("%Y-%m-%d")
f = open(f"{current_date}.csv", "w+", newline='')
lnwriter = csv.writer(f)

while True:
    ret, frame = video_capture.read()
    if not ret:
        break

    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

    # Detect faces
    face_locs = face_recognition.face_locations(rgb_small_frame)
    face_encs = face_recognition.face_encodings(rgb_small_frame, face_locs)

    for face_encoding in face_encs:
        matches = face_recognition.compare_faces(known_faces_encodings, face_encoding)
        face_distances = face_recognition.face_distance(known_faces_encodings, face_encoding)

        name = "Unknown"  # default

        if len(face_distances) > 0:
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = known_faces_names[best_match_index]

        # Show name on screen
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(frame, name, (10, 100), font, 1.5, (255, 0, 0), 3)

        # Mark attendance
        if name != "Unknown" and name in students:
            students.remove(name)
            current_time = datetime.now().strftime("%H:%M:%S")
            lnwriter.writerow([name, current_time])
            print(f"{name} marked present at {current_time}")

    cv2.imshow("Attendance System", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video_capture.release()
cv2.destroyAllWindows()
f.close()