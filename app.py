import os
import warnings
import logging

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", module="tensorflow")
warnings.filterwarnings("ignore", module="tf_keras")

logging.getLogger("tensorflow").setLevel(logging.ERROR)
logging.getLogger("tf_keras").setLevel(logging.ERROR)

import customtkinter as ctk
from PIL import Image, ImageTk
import cv2
import time
import storage
from tkinter import filedialog
from face_utils import detect_faces, crop_face, extract_embedding, verify_face


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

SUCCESS = "#34c759"
ERROR = "#f25f5f"
INFO = "#3498db"

class FaceAuthGUI(ctk.CTk):

    def __init__(self):
        super().__init__()

        if not os.path.exists(storage.ADMIN_PW_PATH):
            self.first_run_admin_setup()

        self.title("Biometric Authentication System")
        self.geometry("780x640")

        self.cap = cv2.VideoCapture(0)
        self.db = storage.load_db()

        # Logging throttle: minimum seconds between logs per identity
        self.log_interval = 1.0
        self._last_log = {}

        self.running = True
        self.is_admin = False
        self.mode = "AUTH"

        # ---------------- Video ----------------
        self.video = ctk.CTkLabel(self, text="")
        self.video.pack(padx=10, pady=10)

        # ---------------- Status ----------------
        self.status = ctk.CTkLabel(self, text="Mode: AUTH", height=28)
        self.status.pack(fill="x", padx=10)

        # ---------------- Controls ----------------
        bar = ctk.CTkFrame(self)
        bar.pack(pady=10)

        ctk.CTkButton(bar, text="Admin Login", fg_color="#ffa500",
                      command=self.admin_login).pack(side="left", padx=6)

        ctk.CTkButton(bar, text="Enroll User", fg_color=SUCCESS,
                      command=self.enroll_window).pack(side="left", padx=6)

        ctk.CTkButton(bar, text="Open Log", fg_color="#9b59b6",
                      command=self.open_log).pack(side="left", padx=6)

        self.after(10, self.update_frame)

    # ================= VIDEO LOOP =================
    def update_frame(self):
        if not self.running:
            return
        
        ret, frame = self.cap.read()
        if ret:
            faces = detect_faces(frame)

            for (x, y, w, h) in faces:
                face = crop_face(frame, (x, y, w, h))
                emb = extract_embedding(face)

                if emb:
                    user, dist = verify_face(emb, self.db)
                    ok = user != "Unknown"
                    color = (0, 255, 0) if ok else (0, 0, 255)

                    cv2.rectangle(frame, (x,y), (x+w,y+h), color, 2)
                    cv2.putText(frame, f"{user} ({dist:.2f})",
                                (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

                    now_ts = time.time()
                    key = user if user else "Unknown"
                    last = self._last_log.get(key, 0)
                    if now_ts - last >= self.log_interval:
                        storage.log_authentication(user, result=("success" if ok else "fail"), confidence=dist)
                        self._last_log[key] = now_ts


            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = ImageTk.PhotoImage(Image.fromarray(rgb))
            self.video.configure(image=img)
            self.video.image = img

        self.after(30, self.update_frame)

    # ================= ADMIN =================
    def admin_login(self):
        win = ctk.CTkToplevel(self)
        win.title("Admin Login")
        win.geometry("320x200")
        win.grab_set()

        entry = ctk.CTkEntry(win, show="*", placeholder_text="Admin password")
        entry.pack(pady=20, padx=20, fill="x")

        def submit():
            if storage.verify_admin(entry.get()):
                self.is_admin = True
                self.status.configure(text="Admin authenticated", fg_color=SUCCESS)
                win.destroy()
            else:
                self.status.configure(text="Admin authentication failed", fg_color=ERROR)
                entry.delete(0, 'end')

        ctk.CTkButton(win, text="Login", command=submit).pack(pady=10)

    def first_run_admin_setup(self):
        win = ctk.CTkToplevel(self)
        win.title("Set Admin Password")
        win.geometry("360x200")
        win.grab_set()

        lbl = ctk.CTkLabel(win, text="No admin password found.\nPlease set a new password:")
        lbl.pack(pady=12, padx=12)

        pw_entry = ctk.CTkEntry(win, show="*", placeholder_text="Enter password")
        pw_entry.pack(pady=6, padx=12, fill="x")

        pw_confirm = ctk.CTkEntry(win, show="*", placeholder_text="Confirm password")
        pw_confirm.pack(pady=6, padx=12, fill="x")

        def set_pw():
            pw = pw_entry.get().strip()
            confirm = pw_confirm.get().strip()
            if not pw:
                self.status.configure(text="Password cannot be empty", fg_color=ERROR)
                return
            if pw != confirm:
                self.status.configure(text="Passwords do not match", fg_color=ERROR)
                return
            # Set hashed admin password
            storage.set_admin_password(pw)
            self.status.configure(text="Admin password set. Please log in.", fg_color=SUCCESS)
            win.grab_release()
            win.destroy()

        btn_frame = ctk.CTkFrame(win)
        btn_frame.pack(pady=10)

        ctk.CTkButton(btn_frame, text="Set Password", fg_color=SUCCESS, command=set_pw).pack(side="left", padx=6)

    # ================= ENROLL =================
    def enroll_window(self):
        if not self.is_admin:
            self.status.configure(text="Admin login required", fg_color=ERROR)
            return

        win = ctk.CTkToplevel(self)
        win.title("Enroll User")
        win.geometry("360x300")
        win.grab_set()

        user_entry = ctk.CTkEntry(win, placeholder_text="Username")
        user_entry.pack(pady=10, padx=20, fill="x")

        def capture():
            self.prompt_capture_count(user_entry.get(), win)

        def upload():
            self.upload_images(user_entry.get())
            win.destroy()

        ctk.CTkButton(win, text="Capture from Camera", fg_color=SUCCESS,
                      command=capture).pack(pady=8)

        ctk.CTkButton(win, text="Upload Images", fg_color="#2fa3f7",
                      command=upload).pack(pady=8)

    def capture_samples(self, username, win, target=5):
        if not username:
            self.status.configure(text="Username required", fg_color=ERROR)
            return

        collected = 0

        progress_win = ctk.CTkToplevel(self)
        progress_win.title("Capturing samples")
        progress_win.geometry("340x120")
        progress_win.grab_set()

        lbl = ctk.CTkLabel(progress_win, text=f"Collected {collected}/{target}")
        lbl.pack(pady=12, padx=12)

        def finish(success=True):
            try:
                progress_win.grab_release()
            except Exception:
                pass
            progress_win.destroy()
            if success:
                storage.log_enrollment(username, "camera", collected)
                self.db = storage.load_db()
                self.status.configure(text=f"{username} enrolled ({collected})", fg_color=SUCCESS)
                win.destroy()
            else:
                self.status.configure(text="Enrollment cancelled", fg_color=ERROR)

        cancel_btn = ctk.CTkButton(progress_win, text="Cancel", fg_color=ERROR,
                                  command=lambda: finish(False))
        cancel_btn.pack(pady=6)

        def do_capture():
            nonlocal collected
            ret, frame = self.cap.read()
            if not ret:
                self.after(250, do_capture)
                return

            faces = detect_faces(frame)
            if len(faces) == 0:
                self.status.configure(text="No face detected. Adjust your position.", fg_color=ERROR)
            elif len(faces) > 1:
                self.status.configure(text="Multiple faces detected. Ensure only one face.", fg_color=ERROR)
            else:
                face = crop_face(frame, faces[0])
                emb = extract_embedding(face)
                if emb:
                    storage.add_user(None, username, emb)
                    collected += 1
                    lbl.configure(text=f"Collected {collected}/{target}")
                    
            if collected >= target:
                finish(True)
                return

            self.after(300, do_capture)

        # Start capturing asynchronously so UI stays responsive
        self.after(0, do_capture)

    def prompt_capture_count(self, username, win):
        if not username:
            self.status.configure(text="Username required", fg_color=ERROR)
            return

        prompt = ctk.CTkToplevel(self)
        prompt.title("Number of samples")
        prompt.geometry("300x140")
        prompt.grab_set()

        lbl = ctk.CTkLabel(prompt, text="Enter number of samples to capture:")
        lbl.pack(pady=(12, 6), padx=12)

        entry = ctk.CTkEntry(prompt)
        entry.insert(0, "5")
        entry.pack(padx=12, fill="x")

        def start():
            val = entry.get().strip()
            try:
                n = int(val)
                if n <= 0:
                    raise ValueError
            except Exception:
                self.status.configure(text="Enter a valid positive number", fg_color=ERROR)
                return
            try:
                prompt.grab_release()
            except Exception:
                pass
            prompt.destroy()
            self.capture_samples(username, win, target=n)

        def cancel():
            try:
                prompt.grab_release()
            except Exception:
                pass
            prompt.destroy()

        btn_frame = ctk.CTkFrame(prompt)
        btn_frame.pack(pady=10)

        ctk.CTkButton(btn_frame, text="Start", fg_color=SUCCESS, command=start).pack(side="left", padx=6)
        ctk.CTkButton(btn_frame, text="Cancel", fg_color=ERROR, command=cancel).pack(side="left", padx=6)

    def upload_images(self, username):
        if not username:
            self.status.configure(text="Username required", fg_color=ERROR)
            return

        folder = filedialog.askdirectory(title="Select folder with face images")

        if not folder:
            return

        files = [f for f in os.listdir(folder)
                 if f.lower().endswith((".jpg", ".jpeg", ".png")) and os.path.isfile(os.path.join(folder, f))]

        if not files:
            self.status.configure(text="No image files found in folder", fg_color=ERROR)
            return

        total = len(files)
        added = 0
        skipped = 0
        idx = 0

        progress_win = ctk.CTkToplevel(self)
        progress_win.title("Uploading images")
        progress_win.geometry("420x140")
        progress_win.grab_set()

        progress_label = ctk.CTkLabel(progress_win, text=f"Processed 0/{total} — Added 0, Skipped 0")
        progress_label.pack(pady=12, padx=12)

        def process_next():
            nonlocal idx, added, skipped
            if idx >= total:
                storage.log_enrollment(username, "upload-folder", added)
                self.db = storage.load_db()
                progress_win.grab_release()
                progress_win.destroy()
                if added > 0:
                    self.status.configure(
                        text=f"{added} images enrolled for {username} ({skipped} skipped)",
                        fg_color=SUCCESS
                    )
                else:
                    self.status.configure(
                        text="No valid faces found in folder",
                        fg_color=ERROR
                    )
                return

            img_name = files[idx]
            img_path = os.path.join(folder, img_name)

            try:
                embedding = extract_embedding(img_path)
                if embedding is None:
                    skipped += 1
                else:
                    storage.add_user(None, username, embedding)
                    added += 1
            except ValueError:
                skipped += 1

            idx += 1
            progress_label.configure(text=f"Processed {idx}/{total} — Added {added}, Skipped {skipped}")
            self.after(100, process_next)

        # start async processing to keep UI responsive
        self.after(0, process_next)

    def open_log(self):
        if os.name == "nt":
            os.startfile(storage.LOG_PATH)

    def on_close(self):
        self.running = False
        try:
            self.cap.release()
        except Exception as e:
            logging.error(f"Error releasing camera: {e}")
        
        try:
            self.destroy()
        except Exception as e:
            logging.error(f"Error closing application: {e}")

if __name__ == "__main__":
    app = FaceAuthGUI()
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()
