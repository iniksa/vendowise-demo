
import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os

st.set_page_config(page_title="VendoWise AI Risk Forecast", layout="wide")

# --- Logo ---
if os.path.exists("Iniksa-TM.png"):
    st.image("Iniksa-TM.png", use_container_width=True)

# --- Load Model ---
@st.cache_resource
def load_model():
    return joblib.load("mock_supplier_risk_model.pkl")

model = load_model()

# --- Tabs ---
tab1, tab2 = st.tabs(["📊 Dashboard", "🤖 AI Risk Forecast"])

# --- Tab 1: Dashboard with File Upload ---
with tab1:
    st.header("📁 Supplier Data Upload")
    uploaded_file = st.file_uploader("Upload Supplier CSV", type=["csv"])
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.success("✅ File uploaded successfully.")
        st.dataframe(df, use_container_width=True)

        if "Supplier" in df.columns and "Avg_Delay_Days" in df.columns and "Rejection_Rate" in df.columns:
            st.subheader("📉 Risk Prediction Preview")
            X = df[["Avg_Delay_Days", "Rejection_Rate"]]
            predictions = model.predict(X)
            df["Risk"] = np.where(predictions == 1, "🔴 High", "🟢 Low")
            st.dataframe(df, use_container_width=True)

# --- Tab 2: AI Risk Forecast ---
with tab2:
    st.header("🔍 Simulate Supplier Risk")
    avg_delay = st.slider("Average Delay (days)", 0, 20, 5)
    rejection_rate = st.slider("Rejection Rate", 0.0, 0.2, 0.05)

    input_data = np.array([[avg_delay, rejection_rate]])
    prediction = model.predict(input_data)[0]

    if prediction == 1:
        st.error("⚠️ Predicted Risk: High 🔴")
    else:
        st.success("✅ Predicted Risk: Low 🟢")

    if st.button("🔔 Smart Alert"):
        if prediction == 1:
            st.warning("🚨 Alert: This supplier poses a HIGH risk based on delay & rejection history.")
        else:
            st.info("✅ This supplier is within safe performance range.")

