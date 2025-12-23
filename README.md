# Biometric Authentication System (Face Recognition)

A desktop GUI application for face-based biometric authentication and enrollment. Uses a webcam to authenticate users and allows administrators to enroll new users by capturing samples or uploading image folders.

**Status:** Prototype — intended for local use and testing.

**Contents**
- `app.py` — main GUI application
- `face_utils.py` — face detection / embedding helpers (project-specific)
- `storage.py` — persistence for users, encodings and logs
- `data/`, `dataset/` — project datasets (may be large)

**Core Features**
- Live webcam authentication with bounding-box overlay and confidence score
- Admin login to access enrollment
- Enroll via camera capture (configurable sample count) or upload image folders
- Asynchronous, non-blocking enrollment and upload with progress dialogs
- Logging of authentication and enrollment events

**Requirements**
- Python 3.8+
- A working webcam for capture
- Recommended packages (install via pip):
  - `customtkinter`
  - `opencv-python`
  - `Pillow`
  - `numpy`
  - `tensorflow` or `tensorflow-cpu` (depending on your hardware)

Example quick install:

```bash
python -m venv .venv
.venv\Scripts\activate    # Windows
pip install --upgrade pip
pip install customtkinter opencv-python Pillow numpy tensorflow
```

If you prefer, create a `requirements.txt` and run `pip install -r requirements.txt`.

**Run the app**

```bash
python app.py
```

The GUI will open and start the webcam feed.

**Usage**

- Mode: The status bar shows current mode and messages.
- Admin Login: Click "Admin Login" and enter the admin password configured in `storage.py`.
- Enroll User: After admin login, click "Enroll User".
  - "Capture from Camera": prompts for the number of samples, then captures that many valid face embeddings (non-blocking).
  - "Upload Images": pick a folder containing face images; files are processed one-by-one with a progress dialog.
- Open Log: Opens the authentication/enrollment log file (Windows only uses `os.startfile`).

**Data and Storage**
- `storage.py` manages loading/saving encodings and logs. Inspect it to see where files are written (e.g., `data/`, `logs/`, or configured paths).
- Large datasets and generated encodings are ignored by the included `.gitignore` by default. If you want to track `data/`, remove it from `.gitignore`.

**Tips & Troubleshooting**
- If the camera doesn't open: check other apps using the webcam, or change `cv2.VideoCapture(0)` index.
- If face embeddings fail or TensorFlow errors appear: ensure `tensorflow` is installed and that your GPU drivers match the installed TF version. For CPU-only systems, `tensorflow-cpu` is safer.
- Slow UI during model load: start the app, wait a few seconds for models to initialize before attempting capture.
- If images aren't detected during upload, verify image formats (`.jpg`, `.jpeg`, `.png`) and that faces are clearly visible.

**Contributing**
- Suggestions, bug reports, and PRs are welcome. Please open issues describing your environment and steps to reproduce.

**Security & Privacy**
- This project stores face embeddings and logs locally. Treat these artifacts as sensitive personal data.
- Do not deploy this prototype in production without reviewing security, privacy, and legal implications.

**License**
- No license is included by default. Add a `LICENSE` file (e.g., MIT) if you want to make this project open-source.

**Acknowledgements**
- Built with `OpenCV`, `TensorFlow`, and `CustomTkinter`.

