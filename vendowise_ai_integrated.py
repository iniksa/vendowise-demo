import streamlit as st
import joblib
import numpy as np

@st.cache_resource
def load_model():
    return joblib.load("mock_supplier_risk_model.pkl")

model = load_model()

st.sidebar.header("Supplier Risk Prediction")

avg_delay = st.sidebar.slider("Average Delay (days)", 0, 20, 5)
rejection_rate = st.sidebar.slider("Rejection Rate", 0.0, 0.2, 0.05)

input_data = np.array([[avg_delay, rejection_rate]])
prediction = model.predict(input_data)[0]

st.markdown("### 🔍 Risk Forecast")
st.write("📊 Predicted Risk:", "**High Risk 🔴**" if prediction == 1 else "**Low Risk 🟢**")
