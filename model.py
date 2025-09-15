import joblib
import pandas as pd
import streamlit as st

@st.cache_resource
def load_model():
    try:
        model = joblib.load("Final_RF_SMOTE_Model.pkl")
    except:
        model = None
    return model

@st.cache_data
def load_kt_data():
    try:
        df = pd.read_excel("Predicted_KT_Students.xlsx")
    except:
        df = pd.DataFrame(columns=["Roll No", "Name", "KT_Prob"])
    return df
