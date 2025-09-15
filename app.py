# app.py
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import json
import os

from auth import auth_admin, auth_student
from model import load_model, load_kt_data
from data import initialize_data
from admin_view import admin_dashboard
from student_view import student_portal
from dotenv import load_dotenv

# Load local .env variables
#load_dotenv()

# ------------------
# Firebase Init
# ------------------
# ------------------
# Firebase Init
# ------------------
if not firebase_admin._apps:
    try:
        # On Streamlit Cloud: FIREBASE_KEY is already a dict
        firebase_key = st.secrets["FIREBASE_KEY"]
        cred = credentials.Certificate(firebase_key)
        firebase_admin.initialize_app(cred)
        st.success("✅ Firebase initialized with Streamlit secrets")
    except Exception as e:
        st.warning(f"⚠️ Falling back to local JSON because secrets failed: {e}")
        from dotenv import load_dotenv
        load_dotenv()
        cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "pydb-a357b-firebase-adminsdk-38foo-4bbf3fffcd.json")
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)



db = firestore.client()

# ------------------
# App Init
# ------------------
st.title("Student Portal with KT Prediction")

initialize_data()
final_model = load_model()
kt_data = load_kt_data()

# ------------------
# Helpers for persistent session
# ------------------
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

# ------------------
# Session Persistence
# ------------------
if "user" not in st.session_state:
    st.session_state.user = load_session()  # load from file if exists

# ------------------
# Login / Main
# ------------------
if st.session_state.user is None:
    st.header("Login")

    mode = st.radio("Login as", ["Student", "Admin"])
    if mode == "Student":
        st.subheader("🎓 Student Login")
    else:
        st.subheader("🛡️ Admin Login")
        
    if mode == "Admin":
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login as Admin"):
            if auth_admin(username, password):
                user = {"role": "admin", "username": username}
                st.session_state.user = user
                save_session(user)   # ✅ persist login
                st.rerun()
            else:
                st.error("Invalid admin credentials")

    else:  # Student login
        rollno = st.number_input("Roll No", min_value=14001, max_value=14067, step=1)
        password = st.text_input("Password (surname in lowercase)", type="password")
        if st.button("Login as Student"):
            if auth_student(rollno, password):
                user = {"role": "student", "rollno": int(rollno)}
                st.session_state.user = user
                save_session(user)   # ✅ persist login
                st.rerun()
            else:
                st.error("Invalid student credentials")

else:
    user = st.session_state.user
    if user["role"] == "admin":
        admin_dashboard(kt_data)
    else:
        student_portal(user["rollno"], kt_data)

    # ✅ IMPORTANT: make sure your existing logout buttons in admin/student
    # also call `clear_session()` before rerun
