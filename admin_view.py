import streamlit as st
import pandas as pd
import datetime
from model import load_model
from data import get_student_record
from firebase_admin import firestore
from chat_ui import inject_css
from utils import clear_session  # make sure this is imported at top
from streamlit_autorefresh import st_autorefresh

def fetch_chat(chat_id, limit=30, before_time=None):
    from utils import get_chat_messages
    return get_chat_messages(chat_id, limit, before_time)

# --- Helper to format time ---
def _format_time(ts):
    try:
        if hasattr(ts, "to_pydatetime"):
            dt = ts.to_pydatetime()
        else:
            dt = ts
        return dt.strftime("%I:%M %p")
    except Exception:
        return ""


def admin_dashboard(kt_data):
    st.header("👨‍🏫 Admin Dashboard")
    inject_css()
    
    # Tabs / Buttons
    st.markdown("---")
    
    db = firestore.client()
    
    nav1, nav2, nav3, nav4, nav5 = st.columns(5)

    if nav1.button("📊"): 
        st.session_state.admin_nav = "KT Predictions"; st.rerun()
    if nav2.button("📑"): 
        st.session_state.admin_nav = "Student Performance Analysis"; st.rerun()
    if nav3.button("💬"): 
        st.session_state.admin_nav = "Messages"; st.rerun()
    if nav4.button("📢"): 
        st.session_state.admin_nav = "Broadcast"; st.rerun()
    if nav5.button("🔑"): 
        st.session_state.admin_nav = "Student Credentials"; st.rerun()

    # Default section
# Default section
    tab = st.session_state.get("admin_nav", "KT Predictions")

# ========================
# KT Predictions Tab (Upload + Auto Prediction)
# ========================
    if tab == "KT Predictions":

        # ------------------------
        # PART 1: Upload & Predict
        # ------------------------
        st.subheader("📂 Upload Data for KT Prediction")

        uploaded_file = st.file_uploader("Upload Excel/CSV with student marks", type=["xlsx", "csv"])

        if uploaded_file:
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)

            st.write("Preview of uploaded data:")
            st.dataframe(df.head())

            model = load_model()
            if model is None:
                st.error("Model not found. Please train and save Final_RF_SMOTE_Model.pkl")
            else:
                try:
                    features = [
                        "Internal Marks Obtained",
                        "Semester End Marks Obtained",
                        "Total Marks Obtained",
                        "Num_Subjects",
                        "Failed_Subjects",
                        "Min_Marks",
                        "Marks_Var"
                    ]
                    X_new = df[features].fillna(0)
                    df["KT_Prob"] = model.predict_proba(X_new)[:, 1]
                    df["KT_Pred"] = (df["KT_Prob"] >= 0.5).astype(int)

                    st.success("✅ Predictions completed on uploaded file!")
                    cols_to_show = [c for c in ["Roll No", "Name", "KT_Prob", "KT_Pred"] if c in df.columns]
                    st.dataframe(df[cols_to_show])

                    # Download results
                    csv = df.to_csv(index=False).encode("utf-8")
                    st.download_button("⬇️ Download Predictions", csv, "KT_Predictions.csv", "text/csv")
                except Exception as e:
                    st.error(f"Error during prediction: {e}")

        st.divider()

        # ------------------------
        # PART 2: Auto Predict from Local Files
        # ------------------------
        st.subheader("📊 Student KT Predictions (Local Data)")

        try:
            marks_df = pd.read_excel("Students_marks_data.xlsx")
            records_df = pd.read_excel("Students_record.xlsx")

            # 🔹 Ensure marks numeric
            for col in ["Internal Marks Obtained", "Semester End Marks Obtained", "Total Marks Obtained"]:
                if col in marks_df.columns:
                    marks_df[col] = pd.to_numeric(marks_df[col], errors="coerce")

            # Aggregate features
            marks_agg = marks_df.groupby("Roll No").agg({
                "Internal Marks Obtained": "mean",
                "Semester End Marks Obtained": "mean",
                "Total Marks Obtained": "mean"
            }).reset_index()

            num_subjects = marks_df.groupby("Roll No")["Course Title"].count().reset_index(name="Num_Subjects")
            min_marks = marks_df.groupby("Roll No")["Total Marks Obtained"].min().reset_index(name="Min_Marks")
            marks_var = marks_df.groupby("Roll No")["Total Marks Obtained"].var().reset_index(name="Marks_Var")

            failed_subjects = (
                marks_df[
                    (marks_df["Internal Marks Obtained"] <= 9) |
                    (marks_df["Semester End Marks Obtained"] <= 23) |
                    (marks_df["Total Marks Obtained"] < 40)
                ]
                .groupby("Roll No")["Course Title"].count()
                .reset_index(name="Failed_Subjects")
            )

            # Merge features
            df = records_df.merge(marks_agg, on="Roll No", how="left")
            df = df.merge(num_subjects, on="Roll No", how="left")
            df = df.merge(min_marks, on="Roll No", how="left")
            df = df.merge(marks_var, on="Roll No", how="left")
            df = df.merge(failed_subjects, on="Roll No", how="left")
            df = df.fillna(0)

            # 🔹 Prediction
            model = load_model()
            if model is None:
                st.error("Model not found. Please train and save Final_RF_SMOTE_Model.pkl")
            else:
                features = [
                    "Internal Marks Obtained",
                    "Semester End Marks Obtained",
                    "Total Marks Obtained",
                    "Num_Subjects",
                    "Failed_Subjects",
                    "Min_Marks",
                    "Marks_Var"
                ]

                X = df[features].fillna(0)
                df["KT_Prob"] = model.predict_proba(X)[:, 1]
                df["KT_Pred"] = (df["KT_Prob"] >= 0.5).astype(int)

                st.success("✅ KT predictions generated from local files!")

                # Show all predictions
                st.dataframe(df[["Roll No", "Name", "KT_Prob", "KT_Pred"]])

                # Highlight risky students
                st.markdown("### ⚠️ Students at Risk of KT")
                kt_students = df[df["KT_Pred"] == 1][["Roll No", "Name", "KT_Prob"]]
                if not kt_students.empty:
                    st.dataframe(kt_students)
                    csv = kt_students.to_csv(index=False).encode("utf-8")
                    st.download_button("⬇️ Download KT Students", csv, "KT_Students.csv", "text/csv")
                else:
                    st.info("No students predicted at high risk of KT.")

        except Exception as e:
            st.error(f"Error loading predictions: {e}")

    elif tab == "Student Performance Analysis":
        st.subheader("📑 Student Performance Analysis")

        try:
            # Load student records
            records_df = pd.read_excel("Students_record.xlsx")
            marks_df = pd.read_excel("Students_marks_data.xlsx")

            # Dropdown to select student
            student_list = records_df["Name"].astype(str) + " (" + records_df["Roll No"].astype(str) + ")"
            selected = st.selectbox("Select Student", student_list)

            if selected:
                rollno = int(selected.split("(")[-1].strip(")"))

                # ✅ Get updated record (from session if student edited info)
                rec = get_student_record(rollno, kt_data)
                if not rec:
                    st.error("Student record not found.")
                else:
                    st.markdown(f"### 👤 {rec['name']} (Roll No: {rollno})")
                    st.write(f"**Class:** {rec['class']} | **Div:** {rec['div']}")
                    st.write(f"**Mobile:** {st.session_state.get(f'mob_{rollno}', rec['mob'])}")
                    st.write(f"**Address:** {st.session_state.get(f'address_{rollno}', rec['address'])}")

                    st.divider()

                    # ======================
                    # Attendance
                    # ======================
                    st.markdown("### 📈 Attendance Overview")
                    if "attendance" in rec and rec["attendance"]:
                        att_df = pd.DataFrame({
                            "Month": list(rec["attendance"].keys()),
                            "Attendance %": list(rec["attendance"].values())
                        })
                        st.line_chart(att_df.set_index("Month"))
                        st.dataframe(att_df)
                    else:
                        st.warning("No attendance record found for this student.")

                    st.divider()

                    # ======================
                    # Subject-wise Marks
                    # ======================
                    st.markdown("### 📊 Subject-wise Performance")

                    student_marks = marks_df[marks_df["Roll No"] == rollno]
                    if not student_marks.empty:
                        # Show bar chart for marks
                        chart_df = student_marks[["Course Title", "Internal Marks Obtained", "Semester End Marks Obtained", "Total Marks Obtained"]]

                        st.bar_chart(chart_df.set_index("Course Title")[["Internal Marks Obtained", "Semester End Marks Obtained"]])
                        st.dataframe(chart_df)
                    else:
                        st.warning("No marks record found for this student.")
        except Exception as e:
            st.error(f"Error loading student performance: {e}")

    # ========================
    # Messages Tab
    # ========================
# ========================
# Messages Tab
# ========================
    elif tab == 'Messages':
        st.subheader("💬 Chat with Students")

        # --- Select Student ---
        try:
            df = pd.read_excel("Students_record.xlsx")
            rollnos = df["Roll No"].astype(str).tolist()
        except Exception:
            rollnos = []

        selected_roll = st.selectbox("Select Student Roll No", rollnos)

        if selected_roll:
            try:
                sel_roll_int = int(selected_roll)
            except Exception:
                sel_roll_int = selected_roll

            rec = get_student_record(sel_roll_int, kt_data)
            if rec is None:
                st.error("Student record not found.")
            else:
                st.markdown(f"### Chat with {rec['name']} (Roll {selected_roll})")

                chat_id = f"{selected_roll}_admin"
                st_autorefresh(interval=5000, limit=10000, key=f"refresh_{chat_id}")

                # First load of messages
                if f"chat_messages_{chat_id}" not in st.session_state:
                    msgs_page, oldest = fetch_chat(chat_id, limit=30)
                    st.session_state[f"chat_messages_{chat_id}"] = msgs_page
                    st.session_state[f"chat_oldest_time_{chat_id}"] = oldest
                else:
                    msgs_page = st.session_state[f"chat_messages_{chat_id}"]
                    oldest = st.session_state[f"chat_oldest_time_{chat_id}"]

                # Delete all chat
                if st.button("🗑️ Delete All Chat", key=f"del_all_{selected_roll}"):
                    try:
                        msgs_ref = db.collection("chats").document(chat_id).collection("messages").stream()
                        for m in msgs_ref:
                            db.collection("chats").document(chat_id).collection("messages").document(m.id).delete()
                        st.success("All chat messages deleted.")
                        st.session_state[f"chat_messages_{chat_id}"] = []
                        st.session_state[f"chat_oldest_time_{chat_id}"] = None
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to delete all chat: {e}")

                msgs = st.session_state.get(f"chat_messages_{chat_id}", [])

                # Button to load older messages
                if st.session_state.get(f"chat_oldest_time_{chat_id}"):
                    if st.button("⬇ Load older messages", key=f"load_older_{chat_id}"):
                        older_msgs, new_oldest = get_chat_messages(chat_id, limit=30, before_time=st.session_state[f"chat_oldest_time_{chat_id}"])
                        if older_msgs:
                            st.session_state[f"chat_messages_{chat_id}"] = older_msgs + st.session_state[f"chat_messages_{chat_id}"]
                            st.session_state[f"chat_oldest_time_{chat_id}"] = new_oldest
                        else:
                            st.info("No older messages.")

                # --- Chat Window ---
                html_msgs = "<div class='chat-room'><div class='chat-window'>"
                last_date = None
                hidden = st.session_state.get(f"hidden_msgs_admin_{selected_roll}", set())

                for m in msgs:
                    if m.get("id") in hidden:
                        continue

                    ts = m.get("time")
                    try:
                        if hasattr(ts, "to_pydatetime"):
                            date_label = ts.to_pydatetime().date()
                        else:
                            date_label = ts.date() if ts else None
                    except Exception:
                        date_label = None

                    if date_label != last_date:
                        if date_label:
                            html_msgs += f"<div class='date-separator'>{date_label.strftime('%A, %d %B %Y')}</div>"
                        last_date = date_label

                    is_me = (m.get("from") == "admin")
                    timestr = _format_time(ts)
                    text = m.get("text", "")
                    bubble_class = "sender" if is_me else "receiver"
                    html_msgs += f'<div class="chat-bubble {bubble_class}">{text}<div class="time">{timestr}</div></div>'

                html_msgs += "</div></div>"
                st.markdown(html_msgs, unsafe_allow_html=True)

                # --- Chat Input ---
                st.markdown("<div class='chat-input'>", unsafe_allow_html=True)
                with st.form(key=f"form_ad_{selected_roll}", clear_on_submit=True):
                    col_text, col_send = st.columns([8, 1])
                    with col_text:
                        new_msg = st.text_input("Type a message", key=f"msg_admin_{selected_roll}", label_visibility="collapsed")
                    with col_send:
                        submit = st.form_submit_button("Send")
                    if submit and new_msg and new_msg.strip():
                        try:
                            db.collection("chats").document(chat_id).collection("messages").add({
                                "from": "admin",
                                "to": selected_roll,
                                "text": new_msg.strip(),
                                "time": datetime.datetime.now(),
                                "edited": False,
                                "deleted": False,
                            })
                            st.session_state[f"chat_messages_{chat_id}"].append({
                                "from": "admin",
                                "to": selected_roll,
                                "text": new_msg.strip(),
                                "time": datetime.datetime.now(),
                                "edited": False,
                                "deleted": False,
                            })
                            st.rerun()
                        except Exception as e:
                            st.error("Failed to send message: " + str(e))
                st.markdown("</div>", unsafe_allow_html=True)  # close chat-input
    # ========================
    # Broadcast Tab
    # ========================
    elif tab == "Broadcast":
        st.subheader("📢 Broadcast Messages")

        header = st.text_input("Broadcast Header")
        msg = st.text_area("Broadcast Message")
        if st.button("Send Broadcast"):
            if header.strip() and msg.strip():
                new_broadcast = {
                    "header": header,
                    "message": msg,
                    "time": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M")
                }
                st.session_state.broadcasts.append(new_broadcast)
                st.success("Broadcast saved & sent!")

        if st.session_state.broadcasts:
            st.markdown("### 📜 Previous Broadcasts")
            for i, bc in enumerate(reversed(st.session_state.broadcasts)):
                st.markdown(f"""
                **📝 {bc['header']}**  
                {bc['message']}  
                ⏰ *{bc['time']}*
                """)
                if st.button(f"❌ Delete", key=f"del_{i}"):
                    st.session_state.broadcasts.pop(len(st.session_state.broadcasts) - 1 - i)
                    st.rerun()
        else:
            st.info("No broadcasts yet.")

    # ========================
    # Credentials Tab
    # ========================
    elif tab == "Student Credentials":
        st.subheader("Manage Student Credentials")
        students = st.session_state.students_df

        roll = st.number_input("Enter Roll No", min_value=14001, max_value=14067, step=1)
        new_pass = st.text_input("New Password")
        if st.button("Update Password"):
            idx = students[students["rollno"] == roll].index
            if not idx.empty:
                st.session_state.students_df.at[idx[0], "password"] = new_pass
                st.success(f"Password updated for Roll No {roll}")
            else:
                st.error("Student not found.")
                
        st.dataframe(students[["rollno", "name", "password"]])
    # ========================

    # ========================
    # Logout bottom
    st.markdown("---")
    if st.button("Logout", key="bottom_logout"):
        if 'user' in st.session_state:
            del st.session_state['user']
        clear_session()   # 🔑 clear .session.json file too
        st.rerun()

