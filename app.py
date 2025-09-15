import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

from auth import auth_admin, auth_student
from model import load_model, load_kt_data
from data import initialize_data
from admin_view import admin_dashboard
from student_view import student_portal

# Load local .env variables
load_dotenv()

# ------------------
# Firebase Init (using JSON file directly)
# ------------------
if not firebase_admin._apps:
    cred = credentials.Certificate("pydb-a357b-firebase-adminsdk-38foo-4bbf3fffcd.json")
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
# Session Management (per role, per device)
# ------------------
def save_session(user, role):
    st.session_state[f"{role}_user"] = user   # stored only on that device/browser

def load_session(role):
    return st.session_state.get(f"{role}_user", None)

def clear_session(role):
    key = f"{role}_user"
    if key in st.session_state:
        del st.session_state[key]

# Ensure session keys exist
if "student_user" not in st.session_state:
    st.session_state.student_user = None
if "admin_user" not in st.session_state:
    st.session_state.admin_user = None

# ------------------
# Login / Main
# ------------------
student_user = load_session("student")
admin_user = load_session("admin")

if not (student_user or admin_user):
    st.header("Login")

    mode = st.radio("Login as", ["Student", "Admin"])
    if mode == "Admin":
        st.subheader("🛡️ Admin Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login as Admin"):
            if auth_admin(username, password):
                user = {"role": "admin", "username": username}
                save_session(user, "admin")
                st.rerun()
            else:
                st.error("Invalid admin credentials")

    else:  # Student login
        st.subheader("🎓 Student Login")
        rollno = st.number_input("Roll No", min_value=14001, max_value=14067, step=1)
        password = st.text_input("Password (surname in lowercase)", type="password")
        if st.button("Login as Student"):
            if auth_student(rollno, password):
                user = {"role": "student", "rollno": int(rollno)}
                save_session(user, "student")
                st.rerun()
            else:
                st.error("Invalid student credentials")

else:
    if admin_user:
        admin_dashboard(kt_data)
        if st.button("🔓 Logout (Admin)"):
            clear_session("admin")
            st.rerun()

    elif student_user:
        student_portal(student_user["rollno"], kt_data)
        if st.button("🔓 Logout (Student)"):
            clear_session("student")
            st.rerun()
