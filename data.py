import streamlit as st
import pandas as pd
import numpy as np


def initialize_data():
    if 'initialized' in st.session_state:
        return
    st.session_state.initialized = True
    
    rollnos = list(range(14001, 14068))
    students = []
    for i, r in enumerate(rollnos, start=1):
        name = f"student{i}"
        students.append({
            'rollno': r,
            'name': name,
            'password': name.lower(),
            'class': 'FY-IT',
            'mob': f'9{700000000 + i}',
            'psid': f'PS{r}',
            'div': 'A' if i % 2 == 0 else 'B',
            'dob': f'2004-0{(i%9)+1}-0{(i%27)+1}',
            'address': f'Address line {i}',
        })
    st.session_state.students_df = pd.DataFrame(students)

    subjects = ['Math', 'Physics', 'Chemistry', 'English', 'CS']
    marks = []
    for r in rollnos:
        row = {'rollno': r}
        for s in subjects:
            row[s] = int(np.clip(np.random.normal(65, 12), 30, 95))
        marks.append(row)
    st.session_state.marks_df = pd.DataFrame(marks)

    att_records = {}
    months = [f"M{i}" for i in range(1, 13)]
    for r in rollnos:
        att_records[r] = {m: int(np.clip(np.random.normal(80, 8), 40, 100)) for m in months}
    st.session_state.attendance = att_records

    st.session_state.messages = {r: [] for r in rollnos}
    st.session_state.broadcasts = []
    st.session_state.help_requests = []

def get_student_record(rollno, kt_data=None):
    df = st.session_state.students_df
    row = df[df['rollno'] == rollno]
    if row.empty: return None

    rec = row.iloc[0].to_dict()
    rec['marks'] = st.session_state.marks_df[st.session_state.marks_df['rollno'] == rollno].to_dict('records')[0]
    rec['attendance'] = st.session_state.attendance.get(rollno, {})
    rec['messages'] = st.session_state.messages.get(rollno, [])

    if kt_data is not None and not kt_data.empty:
        kt_row = kt_data[kt_data["Roll No"] == str(rollno)]
        if not kt_row.empty:
            rec['KT_Prob'] = float(kt_row.iloc[0]["KT_Prob"])
            rec['KT_Pred'] = 1 if rec['KT_Prob'] >= 0.5 else 0
    return rec
