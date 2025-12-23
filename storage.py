import logging
import os
from datetime import datetime
import pickle
import warnings

DATA_DIR = os.path.join("data")
DB_PATH = os.path.join(DATA_DIR, "biometric_db.pkl")
LOG_PATH = os.path.join(DATA_DIR, "auth.log")
ADMIN_PW_PATH = os.path.join(DATA_DIR, "admin_pw.txt")

os.makedirs(DATA_DIR, exist_ok=True)

logging.basicConfig(filename=LOG_PATH, level=logging.INFO, format="%(message)s")
warnings.simplefilter("ignore")

def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _sanitize(val, max_len=200):
    if val is None:
        return ""
    s = str(val)
    return s[:max_len]


def log_authentication(user, event='AUTH', result='success', confidence=None):
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "a", encoding='utf-8') as f:
        f.write(f"{now()} | {event} | {_sanitize(user)} | {_sanitize(result)} | {_sanitize(confidence)}\n")

def log_enrollment(user, result, samples=0):
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "a", encoding='utf-8') as f:
        f.write(f"{now()} | ENROLL | {_sanitize(user)} | {_sanitize(result)} | samples={int(samples)}\n")

def load_db():
    try:
        with open(DB_PATH, 'rb') as f:
            db = pickle.load(f)
        return db
    except FileNotFoundError:
        return {}


def save_db(db):
    with open(DB_PATH, 'wb') as f:
        pickle.dump(db, f)


def add_user(_, username, embedding):
    db = load_db()
    db.setdefault(username, []).append(embedding)
    save_db(db)


def verify_admin(password: str) -> bool:
    try:
        if os.path.exists(ADMIN_PW_PATH):
            with open(ADMIN_PW_PATH, 'r', encoding='utf-8') as f:
                stored = f.read().strip()
            return password == stored
        else:
            return password == 'admin'
    except Exception as e:
        logging.error(f"Error verifying admin password: {e}")
        return False
