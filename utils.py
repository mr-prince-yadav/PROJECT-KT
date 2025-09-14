import qrcode
from PIL import Image
import io
import os, json


# session_utils.py

SESSION_FILE = ".session.json"

def save_session(user):
    with open(SESSION_FILE, "w") as f:
        json.dump(user, f)

def load_session():
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, "r") as f:
            return json.load(f)
    return None

def clear_session():
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)

#QR
def generate_qr(data, size=200):
    qr = qrcode.QRCode(box_size=3, border=1)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white").convert('RGB')
    img = img.resize((size, size))
    return img


