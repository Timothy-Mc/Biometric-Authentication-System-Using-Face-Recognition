# Biometric Authentication System (Face Recognition)

A **desktop GUI application** for face-based biometric authentication and enrollment. It uses a webcam to authenticate users and allows administrators to enroll new users via live capture or image folder uploads.  

**Status:** Prototype — for local use and testing only.

---

## Contents
- `app.py` — main GUI application  
- `face_utils.py` — face detection and embedding helpers  
- `storage.py` — persistence for users, embeddings, and logs  
- `data/`, `dataset/` — project datasets (may be large)  

---

## Core Features
- Live webcam authentication with bounding boxes and confidence scores  
- Admin login with hashed password for secure access  
- User enrollment via:
  - **Camera capture** (configurable number of samples)  
  - **Image folder upload** with progress dialog  
- Asynchronous, non-blocking operations to keep the UI responsive  
- Logs authentication and enrollment events for audit and debugging  

---

## Requirements
- Python 3.8+  
- A working webcam  
- Required packages (install via pip):

```text
customtkinter
opencv-python
Pillow
numpy
tensorflow  # or tensorflow-cpu for CPU-only systems
deepface
bcrypt
scipy
```

## Quick install example:

```bash
python -m venv .venv
.venv\Scripts\activate    # Windows
pip install --upgrade pip
pip install customtkinter opencv-python Pillow numpy tensorflow
```

*Optional:* include all packages in requirements.txt for easy installation.

## Running the App

```bash
python app.py
```
- The GUI opens and initializes the webcam feed.
- On first run, you will be prompted to set an admin password.

## Usage

### Modes & Status
- The status bar displays the current mode and messages (authentication, enrollment progress, errors).

### Admin Login
1. Click **Admin Login**.  
2. Enter the admin password (hashed and stored securely).

### Enroll User
After logging in as admin:  
1. Click **Enroll User**.  
2. Choose enrollment method:
   - **Capture from Camera** — specify number of samples, then capture valid face embeddings asynchronously.  
   - **Upload Images** — select a folder; images are processed asynchronously, showing progress and results.

### Open Logs
- Click **Open Log** to view authentication and enrollment logs. On Windows, this uses `os.startfile`.


## Data & Storage
- `storage.py` handles saving/loading embeddings and logs.  
- Default storage paths: `data/` for embeddings and `logs/` for activity logs.  
- Large datasets and generated embeddings are ignored by `.gitignore` by default.

## Tips & Troubleshooting
- Camera issues: ensure no other apps are using the webcam; try changing `cv2.VideoCapture(0)` index.  
- TensorFlow errors: ensure correct installation and GPU drivers. Use `tensorflow-cpu` for CPU-only systems.  
- Slow UI on startup: wait a few seconds for model initialization.  
- Image uploads not detected: use `.jpg`, `.jpeg`, or `.png` images with clear frontal faces.

## Security & Privacy
- Admin passwords are **hashed** (bcrypt).  
- Face embeddings and logs are stored locally; treat as sensitive personal data.  
- This prototype is **not production-ready**; review legal and privacy implications before deploying.


## Contributing
- Bug reports, suggestions, and pull requests are welcome.  
- Please provide details on environment, steps to reproduce, and any errors encountered.


## License
- No license is included by default. Add a `LICENSE` file (e.g., MIT) if open-sourcing
