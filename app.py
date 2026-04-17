import face_recognition
import cv2
import numpy as np
import tkinter as tk
from threading import Thread
from datetime import datetime
from tkinter import filedialog
import sqlite3
import shutil
import os

# ===== LOAD FACES FROM DB =====
def load_faces():
    encodings = []
    names = []

    conn = sqlite3.connect("attendance.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name, image_path FROM students")
    rows = cursor.fetchall()

    for name, path in rows:
        if os.path.exists(path):
            img = face_recognition.load_image_file(path)
            enc = face_recognition.face_encodings(img)
            if len(enc) > 0:
                encodings.append(enc[0])
                names.append(name)

    conn.close()
    return encodings, names

known_faces_encodings, known_faces_names = load_faces()
students = known_faces_names.copy()

running = False

# ===== ADD STUDENT =====
def add_student():
    name = name_entry.get()

    if name == "":
        status_label.config(text="Enter name")
        return

    file_path = filedialog.askopenfilename()

    if file_path:
        new_path = f"faces/{name}.jpg"
        shutil.copy(file_path, new_path)

        conn = sqlite3.connect("attendance.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO students (name, image_path) VALUES (?, ?)", (name, new_path))
        conn.commit()
        conn.close()

        status_label.config(text=f"{name} added")

# ===== CAMERA =====
def run_camera():
    global running
    video_capture = cv2.VideoCapture(0)

    while running:
        ret, frame = video_capture.read()
        if not ret:
            break

        small = cv2.resize(frame, (0,0), fx=0.25, fy=0.25)
        rgb = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)

        face_locs = face_recognition.face_locations(rgb)
        face_encs = face_recognition.face_encodings(rgb, face_locs)

        for (top, right, bottom, left), face_encoding in zip(face_locs, face_encs):

            matches = face_recognition.compare_faces(known_faces_encodings, face_encoding)
            distances = face_recognition.face_distance(known_faces_encodings, face_encoding)

            name = "Unknown"

            if len(distances) > 0:
                best = np.argmin(distances)
                if matches[best]:
                    name = known_faces_names[best]

            top *= 4; right *= 4; bottom *= 4; left *= 4

            color = (0,255,0) if name!="Unknown" else (0,0,255)
            cv2.rectangle(frame,(left,top),(right,bottom),color,3)
            cv2.putText(frame,name,(left,top-10),cv2.FONT_HERSHEY_SIMPLEX,0.8,(255,255,255),2)

            if name!="Unknown" and name in students:
                students.remove(name)
                time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                conn = sqlite3.connect("attendance.db")
                cursor = conn.cursor()
                cursor.execute("INSERT INTO attendance (name, datetime) VALUES (?,?)",(name,time_now))
                conn.commit()
                conn.close()

                status_label.config(text=f"{name} marked")

        cv2.imshow("Camera", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video_capture.release()
    cv2.destroyAllWindows()

# ===== GUI FUNCTIONS =====
def start():
    global running, known_faces_encodings, known_faces_names, students
    if not running:
        known_faces_encodings, known_faces_names = load_faces()
        students = known_faces_names.copy()
        running = True
        Thread(target=run_camera).start()
        status_label.config(text="Running...")

def stop():
    global running
    running = False
    cv2.destroyAllWindows()
    status_label.config(text="Stopped")

# ===== GUI =====
root = tk.Tk()
root.title("Attendance System")
root.geometry("400x400")
root.configure(bg="black")

tk.Label(root,text="Face Attendance",font=("Arial",18,"bold"),fg="white",bg="black").pack(pady=10)

name_entry = tk.Entry(root,width=25)
name_entry.pack(pady=5)

tk.Button(root,text="Add Student",command=add_student,bg="blue",fg="white").pack(pady=5)
tk.Button(root,text="Start",command=start,bg="green",fg="white").pack(pady=5)
tk.Button(root,text="Stop",command=stop,bg="red",fg="white").pack(pady=5)

status_label = tk.Label(root,text="Status: Idle",fg="yellow",bg="black")
status_label.pack(pady=20)

root.mainloop()