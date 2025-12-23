import cv2
from deepface import DeepFace
from scipy.spatial.distance import cosine

CONFIDENCE_THRESHOLD = 0.4

def detect_faces(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    return faces

def crop_face(frame, bbox):
    x, y, w, h = bbox
    return frame[y:y+h, x:x+w]

def extract_embedding(input_data):
    try:
        rep = DeepFace.represent(
            input_data,
            model_name="Facenet",
            enforce_detection=True
        )
        return rep[0]["embedding"]
    except ValueError:
        return None

def verify_face(embedding, db, threshold=CONFIDENCE_THRESHOLD):
    min_dist = float("inf")
    identity = "Unknown"

    for person, embeddings_list in db.items():
        for emb in embeddings_list:
            dist = cosine(embedding, emb)
            if dist < min_dist:
                min_dist = dist
                identity = person

    if min_dist > threshold:
        identity = "Unknown"

    return identity, min_dist
