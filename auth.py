import streamlit as st

def auth_admin(username, password):
    return username == 'prince' and password == 'admin'

def auth_student(rollno, password):
    df = st.session_state.students_df
    row = df[df['rollno'] == rollno]
    if row.empty:
        return False
    return password == row.iloc[0]['password']
