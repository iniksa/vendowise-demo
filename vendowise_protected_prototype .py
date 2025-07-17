
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="VendoWise Dashboard", layout="wide")

# Sidebar
st.sidebar.image("Iniksa-TM.png", width=150)
st.sidebar.title("Your Supplier Risk Intelligence Hub")
nav = st.sidebar.radio("Go to", ["Dashboard", "PO Entry Simulation", "Configuration Panel"])

# Alert thresholds
st.sidebar.header("Alert Thresholds")
max_delay = st.sidebar.slider("Max acceptable delay (days)", 0, 15, 5)
max_reject = st.sidebar.slider("Max rejection rate (%)", 0, 20, 3) / 100
max_payment_terms = st.sidebar.slider("Max payment terms (days)", 15, 90, 45)
min_stock_buffer = st.sidebar.slider("Minimum stock buffer (days)", 0, 30, 10)
max_location_risk = st.sidebar.slider("Max location risk index", 0, 10, 5)

# Sample data
data = pd.DataFrame({
    "Supplier": ["Alpha", "Bravo", "Charlie", "Delta", "Echo"],
    "Avg_Delay_Days": [2, 7, 4, 10, 1],
    "Rejection_Rate": [0.02, 0.07, 0.04, 0.1, 0.01],
    "Payment_Terms": [30, 60, 45, 90, 30],
    "Stock_Buffer": [15, 5, 10, 3, 20],
    "Location_Risk": [3, 6, 4, 8, 2]
})
data["Risk_Score"] = (
    (data["Avg_Delay_Days"] > max_delay) |
    (data["Rejection_Rate"] > max_reject) |
    (data["Payment_Terms"] > max_payment_terms) |
    (data["Stock_Buffer"] < min_stock_buffer) |
    (data["Location_Risk"] > max_location_risk)
).astype(int)

# Dashboard
if nav == "Dashboard":
    st.markdown("## 📊 VendoWise Supplier Risk Dashboard")
    st.dataframe(data)

    st.markdown("### 📉 Average Delay by Supplier")
    fig, ax = plt.subplots()
    ax.bar(data["Supplier"], data["Avg_Delay_Days"])
    ax.axhline(y=max_delay, color="red", linestyle="--", label="Threshold")
    ax.set_ylabel("Avg Delay Days")
    ax.set_title("Average Delay")
    ax.legend()
    st.pyplot(fig)

    st.markdown("### ❌ Rejection Rate by Supplier")
    fig2, ax2 = plt.subplots()
    ax2.bar(data["Supplier"], data["Rejection_Rate"])
    ax2.axhline(y=max_reject, color="red", linestyle="--", label="Threshold")
    ax2.set_ylabel("Rejection Rate")
    ax2.set_title("Rejection Rate")
    ax2.legend()
    st.pyplot(fig2)

elif nav == "PO Entry Simulation":
    st.markdown("## ✏️ PO Entry Simulation")
    supplier = st.selectbox("Select Supplier", data["Supplier"])
    delay = st.number_input("Expected Delay (days)", 0, 30, 5)
    reject = st.number_input("Expected Rejection Rate (%)", 0.0, 20.0, 1.0) / 100
    payment = st.number_input("Payment Terms (days)", 15, 120, 45)
    stock = st.number_input("Available Stock Buffer (days)", 0, 30, 10)
    location = st.slider("Location Risk Index (0–10)", 0, 10, 5)

    risk = "High Risk 🔴" if (
        delay > max_delay or
        reject > max_reject or
        payment > max_payment_terms or
        stock < min_stock_buffer or
        location > max_location_risk
    ) else "Low Risk 🟢"
    st.success(f"Predicted Risk for {supplier}: **{risk}**")

elif nav == "Configuration Panel":
    st.markdown("## ⚙️ Configuration Panel")
    st.write("Customize thresholds and business logic here.")
