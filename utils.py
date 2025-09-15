import qrcode
from PIL import Image
import io
import pandas as pd
import os, json
import streamlit as st
from firebase_admin import firestore

# utils.py

from firebase_admin import firestore
import json, os

CHAT_FILE = "chat_data.json"
PROFILE_FILE = "profile_data.json"

# ---------------- CHAT ----------------
def load_chats():
    if os.path.exists(CHAT_FILE):
        with open(CHAT_FILE, "r") as f:
            return json.load(f)
    return {}

def save_chats(chats):
    with open(CHAT_FILE, "w") as f:
        json.dump(chats, f, indent=2, default=str)

# ---------------- PROFILE ----------------
def load_profiles():
    if os.path.exists(PROFILE_FILE):
        with open(PROFILE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_profiles(profiles):
    with open(PROFILE_FILE, "w") as f:
        json.dump(profiles, f, indent=2, default=str)

def get_chat_messages(chat_id, limit=30, before_time=None):
    """
    Fetch chat messages from Firestore for a given chat_id.
    Returns (messages_list, oldest_timestamp).
    """
    db = firestore.client()
    msgs_ref = db.collection("chats").document(chat_id).collection("messages")

    # Order by time
    query = msgs_ref.order_by("time", direction=firestore.Query.DESCENDING).limit(limit)

    if before_time:
        query = query.where("time", "<", before_time)

    docs = query.stream()
    messages = []
    oldest = None
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        messages.append(data)
        if data.get("time") is not None:
            if oldest is None or data["time"] < oldest:
                oldest = data["time"]

    # Reverse so that earliest comes first
    messages = list(reversed(messages))
    return messages, oldest

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



