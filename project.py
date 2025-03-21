import cv2
import mediapipe as mp
import numpy as np
import time
import os
import json
import tkinter as tk
from tkinter import simpledialog, messagebox, Label, Button, Toplevel, StringVar, OptionMenu, Frame
import random
from PIL import Image, ImageTk
import pywhatkit as kit
import threading

# Setup MediaPipe
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
pose = mp_pose.Pose()

POSES_DIR = "poses"
LEADERBOARD_FILE = "leaderboard.json"
LOGO_PATH = "logo.png"  # Logo file for home screen

if not os.path.exists(POSES_DIR):
    os.makedirs(POSES_DIR)

# Load saved poses
def load_poses():
    poses = {}
    for file in os.listdir(POSES_DIR):
        if file.endswith(".json"):
            with open(os.path.join(POSES_DIR, file), "r") as f:
                poses[file[:-5]] = json.load(f)
    return poses

# Load leaderboard
def load_leaderboard():
    if os.path.exists(LEADERBOARD_FILE):
        with open(LEADERBOARD_FILE, "r") as f:
            return json.load(f)
    return {}

# Save leaderboard
def save_leaderboard(scores):
    with open(LEADERBOARD_FILE, "w") as f:
        json.dump(scores, f)

# Save a new pose with an image
def save_pose(name, landmarks, image):
    with open(os.path.join(POSES_DIR, f"{name}.json"), "w") as f:
        json.dump(landmarks, f)
    img_path = os.path.join(POSES_DIR, f"{name}.png")
    cv2.imwrite(img_path, image)

# Compare two poses
def compare_poses(user_pose, ref_pose):
    return np.mean([np.linalg.norm(np.array(user_pose[k]) - np.array(ref_pose[k])) for k in user_pose.keys()])

# Display saved poses with images
def display_poses():
    poses = load_poses()
    if not poses:
        messagebox.showinfo("No Poses", "No poses saved.")
        return

    pose_window = Toplevel()
    pose_window.title("Saved Poses")
    pose_window.configure(bg="#34495E")

    row, col = 0, 0
    for pose_name in poses.keys():
        frame = Frame(pose_window, bg="#2C3E50", padx=10, pady=10)
        frame.grid(row=row, column=col, padx=10, pady=10)

        img_path = os.path.join(POSES_DIR, f"{pose_name}.png")
        if os.path.exists(img_path):
            img = Image.open(img_path)
            img = img.resize((120, 120))
            img = ImageTk.PhotoImage(img)
            label_img = Label(frame, image=img, bg="#2C3E50")
            label_img.image = img
            label_img.pack()

        Label(frame, text=pose_name, font=("Arial", 12, "bold"), fg="white", bg="#2C3E50").pack()

        col += 1
        if col > 2:
            col = 0
            row += 1

# Main camera loop
def start_camera(mode, ref_pose_name=None):
    cap = cv2.VideoCapture(0)
    poses = load_poses()

    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    last_still_time = None

    if mode == "practice" and poses:
        root = tk.Tk()
        root.withdraw()
        ref_pose_name = simpledialog.askstring("Select Pose", "Enter the pose name to practice:", initialvalue=list(poses.keys())[0])
        root.destroy()
        if not ref_pose_name or ref_pose_name not in poses:
            messagebox.showwarning("Warning", "Pose not available.")
            return

    if mode == "test" and poses:
        ref_pose_name = random.choice(list(poses.keys()))
        messagebox.showinfo("Pose Test", f"Please do the {ref_pose_name} pose")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(frame_rgb)

        if results.pose_landmarks:
            mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
            landmarks = {str(lm): (results.pose_landmarks.landmark[lm].x, results.pose_landmarks.landmark[lm].y) for lm in range(33)}

            if mode == "add_pose":
                if last_still_time is None:
                    last_still_time = time.time()
                elif time.time() - last_still_time > 3:
                    root = tk.Tk()
                    root.withdraw()
                    pose_name = simpledialog.askstring("Pose Name", "Enter pose name:")
                    if pose_name:
                        save_pose(pose_name, landmarks, frame)
                        messagebox.showinfo("Success", f"Pose '{pose_name}' saved!")
                    root.destroy()
                    break

            elif mode == "practice" and ref_pose_name in poses:
                error = compare_poses(landmarks, poses[ref_pose_name])
                color = (0, 255, 0) if error < 0.05 else (0, 0, 255)
                cv2.putText(frame, f"Match: {100 - int(error * 100)}%", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

            elif mode == "test" and ref_pose_name:
                if last_still_time is None:
                    last_still_time = time.time()
                elif time.time() - last_still_time > 3:
                    error = compare_poses(landmarks, poses[ref_pose_name])
                    match_percentage = max(0, 100 - int(error * 100))
                    name = simpledialog.askstring("Save Score", "Enter your name:")
                    if name:
                        leaderboard = load_leaderboard()
                        leaderboard[name] = match_percentage
                        save_leaderboard(leaderboard)
                        messagebox.showinfo("Test Result", f"{name}, your match percentage: {match_percentage}%")
                    break  

                cv2.putText(frame, f"Hold Still: {int(time.time() - last_still_time)}s", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

        else:
            last_still_time = None  

        cv2.imshow('Pose Trainer', frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == ord('b'):
            break

    cap.release()
    cv2.destroyAllWindows()

# Show saved scores
def show_scores():
    leaderboard = load_leaderboard()
    scores = "\n".join([f"{name}: {score}%" for name, score in leaderboard.items()])
    messagebox.showinfo("Leaderboard", scores if scores else "No scores yet.")

# Login function
def login():
    login_window = tk.Tk()
    login_window.title("Login")
    login_window.configure(bg="#2C3E50")

    Label(login_window, text="Username", font=("Arial", 16), bg="#2C3E50", fg="white").pack(pady=5)
    username_entry = tk.Entry(login_window, font=("Arial", 14))
    username_entry.pack(pady=5)

    Label(login_window, text="Password", font=("Arial", 16), bg="#2C3E50", fg="white").pack(pady=5)
    password_entry = tk.Entry(login_window, font=("Arial", 14), show="*")
    password_entry.pack(pady=5)

    def validate_login():
        username = username_entry.get()
        password = password_entry.get()

        if username == "coach" and password == "123":
            login_window.destroy()
            show_coach_menu()
        elif username == "user" and password == "456":
            login_window.destroy()
            show_user_menu()
        else:
            messagebox.showerror("Error", "Invalid Username or Password")

    Button(login_window, text="Login", command=validate_login, font=("Arial", 16), bg="#E74C3C", fg="white").pack(pady=20)
    login_window.mainloop()

# Send WhatsApp message function
def send_whatsapp_message():
    # Get message input from the text box
    message = message_entry.get()
    if message:
        try:
            # Send message to the student's WhatsApp number (+917984783550)
            student_number = "+917984783550"
            # Send the message instantly
            kit.sendwhatmsg_instantly(student_number, message)
            messagebox.showinfo("Message Sent", "Message has been sent to the student.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send message: {e}")
    else:
        messagebox.showwarning("Empty Message", "Please enter a message to send.")

# Function to send the message using pywhatkit
def send_message(student_number, message):
    try:
        # Send the message to WhatsApp using sendwhatmsg (sends it at the current time + 1 minute)
        kit.sendwhatmsg_instantly(student_number, message)  # Adjust time accordingly

        # Inform the user the message is being sent
        messagebox.showinfo("Message Sent", "Message has been sent to the student.")
        # Hide the message input field and show the confirmation
        message_entry.config(state='disabled')  # Disable the entry field after sending
        send_button.config(state='disabled')  # Disable the send button

    except Exception as e:
        messagebox.showerror("Error", f"Failed to send message: {e}")

# Menu for coach
# Menu for coach
def show_coach_menu():
    root = tk.Tk()
    root.title("Pose Trainer - Coach")
    root.geometry("800x600")  # Set the window size
    root.configure(bg="#2C3E50")

    Label(root, text="Pose Trainer - Coach", font=("Arial", 24, "bold"), bg="#2C3E50", fg="#F1C40F").pack(pady=10)

    button_style = {"font": ("Arial", 16, "bold"), "bg": "#E74C3C", "fg": "white"}

    # Add input field for the coach to type the message
    Label(root, text="Enter message for student:", font=("Arial", 16), bg="#2C3E50", fg="white").pack(pady=10)
    global message_entry
    message_entry = tk.Entry(root, font=("Arial", 14), width=40)
    message_entry.pack(pady=10)

    # Add a button to send the message
    global send_button
    send_button = tk.Button(root, text="Send Message", command=send_whatsapp_message, **button_style)
    send_button.pack(pady=10)

    # Add "Add Pose" button for the coach to record new poses
    Button(root, text="Add Pose", command=lambda: start_camera("add_pose"), **button_style).pack(pady=10)

    # Add other coach menu options
    Button(root, text="Display Poses", command=display_poses, **button_style).pack(pady=10)
    Button(root, text="See Scores", command=show_scores, **button_style).pack(pady=10)
    Button(root, text="Exit", command=root.quit, **button_style).pack(pady=10)

    root.mainloop()

# Menu for user
def show_user_menu():
    root = tk.Tk()
    root.title("Pose Trainer - User")
    root.attributes('-fullscreen', True)
    root.configure(bg="#2C3E50")

    if os.path.exists(LOGO_PATH):
        logo = Image.open(LOGO_PATH)
        logo = logo.resize((200, 200))
        logo = ImageTk.PhotoImage(logo)
        logo_label = Label(root, image=logo, bg="#2C3E50")
        logo_label.image = logo
        logo_label.pack(pady=15)

    Label(root, text="Pose Trainer - User", font=("Arial", 24, "bold"), bg="#2C3E50", fg="#F1C40F").pack(pady=10)

    button_style = {"font": ("Arial", 16, "bold"), "bg": "#E74C3C", "fg": "white"}

    Button(root, text="Display Poses", command=display_poses, **button_style).pack(pady=10)
    Button(root, text="Practice Pose", command=lambda: start_camera("practice") if load_poses() else messagebox.showwarning("Warning", "No poses available."), **button_style).pack(pady=10)
    Button(root, text="Test", command=lambda: start_camera("test") if load_poses() else messagebox.showwarning("Warning", "No poses available."), **button_style).pack(pady=10)
    Button(root, text="Show Scores", command=show_scores, **button_style).pack(pady=10)
    Button(root, text="Exit", command=root.quit, **button_style).pack(pady=10)

    root.mainloop()

login()