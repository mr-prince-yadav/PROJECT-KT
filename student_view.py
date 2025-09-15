# student_view.py
import streamlit as st
import altair as alt
import pandas as pd
import numpy as np
from PIL import Image
import io
import base64
import joblib
from utils import load_chats, save_chats, load_profiles, save_profiles
import datetime
from utils import clear_session
from data import get_student_record
from utils import generate_qr
from firebase_admin import firestore
from chat_ui import inject_css
from streamlit_autorefresh import st_autorefresh

# cached chat fetcher
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


def _get_field_with_fallback(rec: dict, rollno: int, keys: list, session_key_prefix: str = None, default=""):
    """
    Try session override first (session_key_prefix + rollno), then rec keys in order.
    keys example: ['name','Name']
    """
    if session_key_prefix:
        sk = f"{session_key_prefix}_{rollno}"
        if sk in st.session_state:
            return st.session_state[sk]
    for k in keys:
        if k in rec and pd.notna(rec.get(k)):
            return rec.get(k)
    return default


def _update_students_df_name(rollno: int, new_name: str):
    """If students_df exists in session_state, update the Name (or name) field for given rollno."""
    if "students_df" not in st.session_state:
        return
    df = st.session_state.students_df
    # detect roll column name and name column name
    roll_cols = [c for c in ["Roll No", "rollno", "RollNo", "roll_no"] if c in df.columns]
    name_cols = [c for c in ["Name", "name", "student_name"] if c in df.columns]

    if not roll_cols or not name_cols:
        return

    roll_col = roll_cols[0]
    name_col = name_cols[0]

    # match type: try convert rollno to the same type as df[roll_col]
    try:
        if pd.api.types.is_integer_dtype(df[roll_col].dtype):
            match_val = int(rollno)
        else:
            match_val = rollno
    except Exception:
        match_val = rollno

    idx = df.index[df[roll_col] == match_val]
    if not idx.empty:
        st.session_state.students_df.at[idx[0], name_col] = new_name

def _update_students_df_field(rollno: int, field: str, value):
    """Generic updater for students_df in session_state"""
    if "students_df" not in st.session_state:
        return
    df = st.session_state.students_df
    roll_col = "rollno" if "rollno" in df.columns else "Roll No"
    idx = df.index[df[roll_col] == rollno]
    if not idx.empty and field in df.columns:
        st.session_state.students_df.at[idx[0], field] = value

def student_portal(rollno, kt_data):
    
    # fetch record (raw from data module)
    rec = get_student_record(rollno, kt_data)
    if rec is None:
        st.error("Student record not found.")
        return

    # Use session overrides or rec fields (try multiple capitalization forms)
    # Fallback defaults
    display_name = _get_field_with_fallback(rec, rollno, ["name", "Name"], session_key_prefix="name", default=f"STUDENT{rollno}")
    display_class = _get_field_with_fallback(rec, rollno, ["class", "Class"], default="FY-IT")
    display_div = _get_field_with_fallback(rec, rollno, ["div", "Div"], default="A")
    display_mob = _get_field_with_fallback(rec, rollno, ["mob", "Mob", "Mobile", "mobile"], default="0000000000")
    display_address = _get_field_with_fallback(rec, rollno, ["address", "Address"], default="Not Provided")
    display_psid = _get_field_with_fallback(rec, rollno, ["psid", "PSID", "Psid"], default=f"PS{rollno}")


    st.header(f"Welcome {display_name} (Roll No: {rollno})")

    # Nav bar
    nav = st.session_state.get('nav', 'home')
    tabs = st.columns(5)

    if tabs[0].button("🏠", key="home"):
        st.session_state.nav = 'home'; st.rerun()
    if tabs[1].button("💬", key="message"):
        st.session_state.nav = 'message'; st.rerun()
    if tabs[2].button("🪪", key="id"):
        st.session_state.nav = 'id'; st.rerun()
    if tabs[3].button("📢", key="broadcast"):
        st.session_state.nav = 'broadcast'; st.rerun()
    if tabs[4].button("👤", key="personal"):
        st.session_state.nav = 'personal'; st.rerun()

    nav = st.session_state.get('nav', 'home')

    # -------------------
    # HOME
    # -------------------
    if nav == 'home':
        # =========================
        # 📈 Attendance Graph (demo / random or session)
        # =========================
        st.subheader("📈 Monthly Attendance")
        try:
            # Try to use rec['attendance'] if present, otherwise random demo
            attendance = rec.get("attendance", None)
            if attendance and isinstance(attendance, dict) and len(attendance) > 0:
                months = list(attendance.keys())
                values = list(attendance.values())
                df_att = pd.DataFrame({"Month": months, "Attendance": values})
            else:
                months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
                values = np.random.randint(60, 100, size=len(months))
                df_att = pd.DataFrame({"Month": months, "Attendance": values})

            st.altair_chart(
                alt.Chart(df_att).mark_line(point=True).encode(
                    x="Month:N",
                    y="Attendance:Q"
                ).properties(title="Monthly Attendance (%)"),
                use_container_width=True
            )
        except Exception as e:
            st.error(f"Error loading attendance: {e}")

        # =========================
        # 📊 Subject Performance
        # =========================
        st.subheader("📊 Subject Performance (Internal + External)")

        try:
            marks_df = pd.read_excel("Students_marks_data.xlsx")
            # ensure Roll No column exists and comparable type
            if "Roll No" in marks_df.columns:
                student_marks = marks_df[marks_df["Roll No"] == rollno]
            elif "rollno" in marks_df.columns:
                student_marks = marks_df[marks_df["rollno"] == rollno]
            else:
                student_marks = pd.DataFrame()

            if not student_marks.empty:
                # select columns safely
                cols = student_marks.columns.tolist()
                int_col = "Internal Marks Obtained" if "Internal Marks Obtained" in cols else ("Internal Marks" if "Internal Marks" in cols else None)
                ext_col = "Semester End Marks Obtained" if "Semester End Marks Obtained" in cols else ("External Marks" if "External Marks" in cols else None)
                tot_col = "Total Marks Obtained" if "Total Marks Obtained" in cols else ("Total Marks" if "Total Marks" in cols else None)

                df_perf = student_marks.copy()
                # rename for internal usage
                rename_map = {}
                if int_col:
                    rename_map[int_col] = "Internal Marks"
                if ext_col:
                    rename_map[ext_col] = "External Marks"
                if tot_col:
                    rename_map[tot_col] = "Total Marks"
                if rename_map:
                    df_perf = df_perf.rename(columns=rename_map)

                # Add pass/fail using rules: internal>9 and external>23 -> pass AND total>=40
                if "Internal Marks" in df_perf.columns and "External Marks" in df_perf.columns and "Total Marks" in df_perf.columns:
                    df_perf["Result"] = df_perf.apply(
                        lambda r: "✅ Pass" if (pd.notna(r["Internal Marks"]) and pd.notna(r["External Marks"]) and pd.notna(r["Total Marks"]) and
                                               (r["Internal Marks"] > 9) and (r["External Marks"] > 23) and (r["Total Marks"] >= 40)) else "❌ Fail",
                        axis=1
                    )
                else:
                    df_perf["Result"] = "N/A"


                # stacked bar (internal + external) if those columns exist
                if "Internal Marks" in df_perf.columns and "External Marks" in df_perf.columns:
                    df_melt = df_perf.melt(id_vars="Course Title", value_vars=["Internal Marks", "External Marks"],
                                           var_name="Exam Type", value_name="Marks")
                    st.altair_chart(
                        alt.Chart(df_melt).mark_bar().encode(
                            x=alt.X("Course Title:N", sort=None),
                            y="Marks:Q",
                            color="Exam Type:N",
                            tooltip=["Course Title", "Exam Type", "Marks"]
                        ).properties(title="Stacked Internal + External Marks"),
                        use_container_width=True
                    )
            else:
                st.warning("No marks found for this student.")
        except Exception as e:
            st.error(f"Error loading subject performance: {e}")

        # =========================
        # 🎯 KT Prediction (uses model file if present)
        # =========================
        st.subheader("🎯 KT Prediction")
        try:
            model = joblib.load("Final_RF_SMOTE_Model.pkl")
            marks_df = pd.read_excel("Students_marks_data.xlsx")
            # fetch student's subjects similarly as above
            if "Roll No" in marks_df.columns:
                student_marks = marks_df[marks_df["Roll No"] == rollno]
            elif "rollno" in marks_df.columns:
                student_marks = marks_df[marks_df["rollno"] == rollno]
            else:
                student_marks = pd.DataFrame()

            if student_marks.empty:
                st.warning("No marks available to predict KT.")
            else:
                # ensure numeric columns exist and coerce
                for col in ["Internal Marks Obtained", "Semester End Marks Obtained", "Total Marks Obtained"]:
                    if col in student_marks.columns:
                        student_marks[col] = pd.to_numeric(student_marks[col], errors="coerce")

                internal_mean = float(student_marks.get("Internal Marks Obtained", pd.Series([0])).mean(skipna=True) or 0.0)
                external_mean = float(student_marks.get("Semester End Marks Obtained", pd.Series([0])).mean(skipna=True) or 0.0)
                total_mean = float(student_marks.get("Total Marks Obtained", pd.Series([0])).mean(skipna=True) or 0.0)
                num_subjects = int(len(student_marks))
                failed_subjects = int((
                    (student_marks.get("Internal Marks Obtained", pd.Series([])) <= 9) |
                    (student_marks.get("Semester End Marks Obtained", pd.Series([])) <= 23) |
                    (student_marks.get("Total Marks Obtained", pd.Series([])) < 40)
                ).sum())
                min_marks = float(student_marks.get("Total Marks Obtained", pd.Series([0])).min(skipna=True) or 0.0)
                marks_var = float(student_marks.get("Total Marks Obtained", pd.Series([0])).var(ddof=0, skipna=True) or 0.0)

                import numpy as _np
                X_row = _np.array([
                    internal_mean,
                    external_mean,
                    total_mean,
                    num_subjects,
                    failed_subjects,
                    min_marks,
                    marks_var
                ], dtype=float).reshape(1, -1)

                prob = float(model.predict_proba(X_row)[0][1])
                pred = int(prob >= 0.5)

                st.markdown(f"**KT Probability:** {prob:.2%}")
                if pred == 1:
                    st.error("⚠️ Predicted: HIGH RISK of KT")
                else:
                    st.success("✅ Predicted: LOW RISK of KT")
                st.progress(min(max(prob, 0.0), 1.0))
        except FileNotFoundError:
            st.info("KT model file not found (Final_RF_SMOTE_Model.pkl). Prediction disabled.")
        except Exception as e:
            st.error(f"Error predicting KT: {e}")

# -------------------
# MESSAGES
# -------------------


# -------------------
# SIMPLE PERSISTENT LOCAL CHAT
# -------------------
    elif nav == "message":
        st.subheader("💬 Messages")

        from utils import load_chats, save_chats
        all_chats = load_chats()

        chat_id = f"chat_{rollno}"
        if chat_id not in all_chats:
            all_chats[chat_id] = []

        # Auto-refresh every 3s
        st_autorefresh(interval=3000, key=f"chat_refresh_admin_{selected_roll}")
        
        # Always reload from disk so new messages appear
        all_chats = load_chats()
        st.session_state[f"chat_{selected_roll}"] = all_chats[chat_id]


        # ✅ Same CSS as admin
        st.markdown("""
        <style>
        .chat-room {
            height:65vh;
            overflow-y:auto;
            padding:10px;
            border:1px solid #ccc;
            border-radius:10px;
        }
        .chat-bubble {
            margin:6px 0;
            padding:8px 12px;
            border-radius:15px;
            max-width:70%;
            position:relative;
            word-wrap:break-word;
        }
        .date-separator {
            text-align:center;
            font-size:12px;
            margin:10px 0;
        }
        
        /* Light mode */
        @media (prefers-color-scheme: light) {
            .sender { background:#dcf8c6; color:#000; margin-left:auto; border:1px solid #b8e6b8; }
            .receiver { background:#ffffff; color:#000; margin-right:auto; border:1px solid #ddd; }
            .time { font-size:10px; color:#555; text-align:right; }
            .date-separator { color:#666; }
        }
        
        /* Dark mode */
        @media (prefers-color-scheme: dark) {
            .sender { background:#075e54; color:#fff; margin-left:auto; border:1px solid #0b8b80; }
            .receiver { background:#2a3942; color:#eaeaea; margin-right:auto; border:1px solid #3a4b53; }
            .time { font-size:10px; color:#aaa; text-align:right; }
            .date-separator { color:#ccc; }
        }
        </style>
        """, unsafe_allow_html=True)
        

        # --- Build chat HTML safely ---
        chat_html = ["<div class='chat-room'>"]
        last_date = None

        for msg in st.session_state[f"chat_{rollno}"]:
            dt = datetime.datetime.fromisoformat(msg["time"])
            msg_date = dt.date()

            # Add date separator if new date
            if msg_date != last_date:
                chat_html.append(
                    f"<div class='date-separator'>{msg_date.strftime('%A, %d %B %Y')}</div>"
                )
                last_date = msg_date

            is_me = (msg["from"] == "student")
            bubble_class = "sender" if is_me else "receiver"


            # 🔑 Strip newlines and avoid nested markdown
            chat_html.append(
                f"<div class='chat-bubble {bubble_class}'>"
                f"{msg['text']}"
                f"<div class='time'>{dt.strftime('%I:%M %p')}</div>"
                f"</div>"
            )

        chat_html.append("</div>")

        # ✅ Render final joined HTML once
        st.markdown("".join(chat_html), unsafe_allow_html=True)

        # --- Input form ---
        with st.form(key=f"form_student_{rollno}", clear_on_submit=True):
            col1, col2 = st.columns([8, 1])
            with col1:
                new_msg = st.text_area("Type message", height=70, label_visibility="collapsed")
            with col2:
                submit = st.form_submit_button("➤")

            if submit and new_msg.strip():
                msg_obj = {
                    "from": "student",
                    "to": "admin",
                    "text": new_msg.strip(),
                    "time": datetime.datetime.now().isoformat()
                }
                st.session_state[f"chat_{rollno}"].append(msg_obj)
                all_chats[chat_id] = st.session_state[f"chat_{rollno}"]
                save_chats(all_chats)
                st.rerun()

        # --- Delete all chat for student ---
        if st.button("🗑️ Delete My Chat", key=f"del_student_{rollno}"):
            st.session_state[f"chat_{rollno}"] = []
            all_chats[chat_id] = []
            save_chats(all_chats)
            st.success("Your chat has been cleared!")
            st.rerun()

  # -------------------
# ID CARD
# -------------------
    elif nav == 'id':
        st.subheader("🎓 Student ID Card")
    
        # Photo
        if f"photo_{rollno}" in st.session_state:
            photo_img = st.session_state[f"photo_{rollno}"]
        else:
            photo_img = Image.new('RGB', (200, 240), color=(200, 200, 200))
    
        bio_photo = io.BytesIO()
        photo_img.save(bio_photo, format="PNG")
        photo_base64 = base64.b64encode(bio_photo.getvalue()).decode("utf-8")
    
        # QR
        qr = generate_qr(display_psid or rec.get("psid", rec.get("PSID", "")))
        bio_qr = io.BytesIO()
        qr.save(bio_qr, format="PNG")
        qr_base64 = base64.b64encode(bio_qr.getvalue()).decode("utf-8")
    
        # ✅ Updated CSS here
        st.markdown("""
        <style>
        .id-card {
          width: 420px;
          border: 2px solid #000;
          border-radius: 12px;
          padding: 12px;
          margin: auto;
          background: #ffffff !important;
          color: #111111 !important;
        }
        .id-card * {
          color: #111111 !important;
          -webkit-text-fill-color: #111111 !important;
        }
        </style>
        """, unsafe_allow_html=True)
    
        # Render HTML
        st.markdown(f"""
        <div class="id-card">
            <div style="text-align:center;font-weight:bold">R.J. COLLEGE of Arts, Science & Commerce</div>
            <div style="display:flex;margin-top:8px">
                <div style="width:120px;height:150px;border:1px solid #999">
                    <img src="data:image/png;base64,{photo_base64}" style="width:100%;height:100%;object-fit:cover"/>
                </div>
                <div style="flex:1;text-align:center;padding-top:10px">
                    <img src="data:image/png;base64,{qr_base64}" width="100"/>
                </div>
                <div style="writing-mode:vertical-rl;transform:rotate(180deg);font-weight:bold;margin-left:6px">ROLL NO: {rollno}</div>
            </div>
            <div style="margin-top:8px;font-size:13px">
                <b>{display_name.upper()}</b><br>
                Class: {display_class}<br>
                Mob: {display_mob}<br>
                PSID: {display_psid}<br>
                Div: {display_div}<br>
                Address: {display_address}
            </div>
            <div style="display:flex;justify-content:space-between;margin-top:12px;font-size:12px">
                <div><b>STUDENT'S SIGN</b></div><div><b>PRINCIPAL</b></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # -------------------
    # BROADCAST
    # -------------------
    elif nav == 'broadcast':
        st.subheader("📢 Broadcasts from Admin")
        if st.session_state.broadcasts:
            for b in reversed(st.session_state.broadcasts):
                st.markdown(f"**📝 {b['header']}**  \n{b['message']}  \n⏰ *{b['time']}*")
        else:
            st.info("No broadcasts yet.")

    # -------------------
    # PERSONAL (profile + edit)
    # -------------------
    elif nav == 'personal':
        st.subheader("👤 Profile")
        col1, col2 = st.columns([1, 3])
        with col1:
            if f"photo_{rollno}" in st.session_state:
                st.image(st.session_state[f"photo_{rollno}"], caption="Student Photo", width=120)
            else:
                img = Image.new('RGB', (200, 240), color=(200, 200, 200))
                st.image(img, caption="Student Photo", width=120)

        with col2:
            st.markdown(f"### {display_name}")
            st.markdown(f"**Class:** {display_class} | **Div:** {display_div}")
            st.markdown(f"**Roll No:** {rollno}")

        st.divider()

        # ----------------
        # Personal Detail expander - now includes name update + photo update
        # ----------------
        with st.expander("📌 Personal Detail", expanded=False):
            # Current values
            current_name = _get_field_with_fallback(rec, rollno, ["name", "Name"], session_key_prefix="name", default="")
            # Name input
            new_name = st.text_input("Student Name", value=current_name, key=f"name_input_{rollno}")

            # Photo upload preview (same as before)
            uploaded_photo = st.file_uploader("Upload Profile Photo", type=["png", "jpg", "jpeg"])
            if uploaded_photo:
                preview_img = Image.open(uploaded_photo)
                st.image(preview_img, caption="Preview (not saved)", width=120)

                colp1, colp2 = st.columns([1, 1])
                with colp1:
                    if st.button("💾 Save Photo", key=f"save_photo_{rollno}"):
                        st.session_state[f"photo_{rollno}"] = preview_img
                        # store in students_df as bytes for admin view
                        bio = io.BytesIO()
                        preview_img.save(bio, format="PNG")
                        _update_students_df_field(rollno, "profile_pic", bio.getvalue())
                        st.success("Profile photo updated!")
                        st.rerun()

                with colp2:
                    if st.button("❌ Remove Photo", key=f"remove_photo_{rollno}"):
                        if f"photo_{rollno}" in st.session_state:
                            del st.session_state[f"photo_{rollno}"]
                        st.success("Profile photo removed!")
                        st.rerun()
            elif f"photo_{rollno}" in st.session_state:
                st.image(st.session_state[f"photo_{rollno}"], caption="Profile Photo", width=120)
                if st.button("❌ Remove Photo", key=f"remove_saved_photo_{rollno}"):
                    del st.session_state[f"photo_{rollno}"]
                    st.success("Profile photo removed!")
                    st.rerun()
            else:
                placeholder = Image.new('RGB', (200, 240), color=(200, 200, 200))
                st.image(placeholder, caption="Student Photo", width=120)

            # Save name button
            if st.button("💾 Save Name", key=f"save_name_{rollno}"):
                cleaned = str(new_name).strip()
                if cleaned == "":
                    st.error("Name cannot be empty.")
                else:
                    st.session_state[f"name_{rollno}"] = cleaned
                    _update_students_df_name(rollno, cleaned)   # updates in students_df
                    st.success("Name updated!")
                    st.rerun()

            # Remove name override
            if st.button("❌ Revert Name to Original", key=f"revert_name_{rollno}"):
                sk = f"name_{rollno}"
                if sk in st.session_state:
                    del st.session_state[sk]
                st.success("Name override removed. Original name restored.")
                st.rerun()

        # Contact Detail
        with st.expander("📞 Contact Detail", expanded=False):
            current_mob = st.session_state.get(f"mob_{rollno}", display_mob)
            current_mob2 = st.session_state.get(f"mob2_{rollno}", "")
            mob1 = st.text_input("Primary Mobile", current_mob, key=f"mob_input_{rollno}")
            mob2 = st.text_input("Additional Mobile", current_mob2, key=f"mob2_input_{rollno}")

            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("💾 Save Contact", key=f"save_contact_{rollno}"):
                    st.session_state[f"mob_{rollno}"] = mob1
                    st.session_state[f"mob2_{rollno}"] = mob2
                    st.success("Contact details updated!")
                    st.rerun()
            with col2:
                if st.button("❌ Remove Contact", key=f"remove_contact_{rollno}"):
                    st.session_state[f"mob_{rollno}"] = ""
                    st.session_state[f"mob2_{rollno}"] = ""
                    st.success("Contact details cleared!")
                    st.rerun()

        # Postal Detail
        with st.expander("🏠 Postal Detail", expanded=False):
            current_address = st.session_state.get(f"address_{rollno}", display_address)
            new_address = st.text_area("Address", current_address, key=f"address_input_{rollno}")

            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("💾 Save Address", key=f"save_address_{rollno}"):
                    st.session_state[f"address_{rollno}"] = new_address
                    _update_students_df_field(rollno, "address", new_address)
                    st.success("Address updated!")
                    st.rerun()

            with col2:
                if st.button("❌ Remove Address", key=f"remove_address_{rollno}"):
                    if f"address_{rollno}" in st.session_state:
                        del st.session_state[f"address_{rollno}"]
                    st.success("Address removed!")
                    st.rerun()

        # Messages expander
        if "messages" in rec:
            with st.expander("💬 Messages", expanded=False):
                for msg in rec["messages"]:
                    st.info(f"📩 {msg['text']}  \n_({msg['time']})_")

        st.divider()
        if st.button("🔓 Log out"):
            if 'user' in st.session_state:
                del st.session_state['user']
            clear_session()
            st.rerun()



    st.markdown("---")
    st.caption("Use the buttons above to navigate.")














