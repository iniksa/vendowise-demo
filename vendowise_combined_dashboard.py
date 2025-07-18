import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import json
import os
from datetime import datetime, timedelta

# ----------------- LOGIN -----------------
def login():
    st.title("🔐 Login Required")
    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")
    if st.button("Login"):
        if user == "admin" and pwd == "admin":
            st.session_state.logged_in = True
        else:
            st.error("Invalid credentials")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login()
    st.stop()
# -----------------------------------------

st.set_page_config(page_title="VendoWise Unified App", layout="wide")
st.sidebar.image("Iniksa-TM.png", width=150)
st.sidebar.title("VendoWise AI Toolkit")
nav = st.sidebar.radio("Navigate to", ["📊 Supplier Risk", "📦 Inventory Risk", "✏️ PO Entry Simulation", "⚙️ Config Panel"])

# -------- Load Configuration --------
config_path = "vendowise_config.json"
default_config = {
    "use_rejected_qty": True,
    "use_payment_terms": True,
    "use_stock_buffer": True,
    "use_location_risk": True,
    "thresholds": {
        "delay_days": 5,
        "rejection_rate": 0.05,
        "payment_terms_days": 60,
        "min_stock_buffer_days": 7,
        "max_location_risk": 6
    }
}

if os.path.exists(config_path):
    with open(config_path) as f:
        config = json.load(f)
else:
    config = default_config

# -------- Load Supplier Data --------
@st.cache_data
def load_supplier_data():
    return pd.read_csv("vendor_data.csv")

@st.cache_data
def load_inventory_data():
    return pd.read_csv("inventory_data.csv")

today = datetime.today()

# ========== TABS ==========

if nav == "📊 Supplier Risk":
    st.header("📊 Supplier Risk Dashboard")
    df = load_supplier_data()
    expected_cols = [
        "Supplier", "Expected Delay (days)", "Rejection Rate",
        "Payment Terms", "Stock Buffer (days)", "Location Risk Index"
    ]
    if not all(col in df.columns for col in expected_cols):
        st.warning("⚠️ Missing columns in vendor_data.csv.")
        st.stop()

    def calculate_risk(row):
        risk_score = 0
        if config["use_rejected_qty"] and row["Rejection Rate"] > config["thresholds"]["rejection_rate"]:
            risk_score += 1
        if config["use_payment_terms"] and row["Payment Terms"] > config["thresholds"]["payment_terms_days"]:
            risk_score += 1
        if config["use_stock_buffer"] and row["Stock Buffer (days)"] < config["thresholds"]["min_stock_buffer_days"]:
            risk_score += 1
        if config["use_location_risk"] and row["Location Risk Index"] > config["thresholds"]["max_location_risk"]:
            risk_score += 1
        if row["Expected Delay (days)"] > config["thresholds"]["delay_days"]:
            risk_score += 1
        return "High Risk 🔴" if risk_score >= 3 else "Low Risk 🟢"

    df["Risk"] = df.apply(calculate_risk, axis=1)
    st.dataframe(df)

    chart_data = df["Risk"].value_counts()
    st.bar_chart(chart_data)

elif nav == "📦 Inventory Risk":
    st.header("📦 Inventory Buffer Risk Forecast")
    df = load_inventory_data()
    if not all(col in df.columns for col in ["Next PO Delivery Date", "Expected Delay (days)", "Current Stock (Qty)", "Daily Avg Consumption", "Buffer Stock (days)"]):
        st.warning("⚠️ Missing columns in inventory_data.csv.")
        st.stop()

    df["Next PO Delivery Date"] = pd.to_datetime(df["Next PO Delivery Date"], errors="coerce")

    def compute_inventory_risk(row):
        if pd.isna(row["Next PO Delivery Date"]):
            return "No PO ❓"
        delivery_date = row["Next PO Delivery Date"] + timedelta(days=row["Expected Delay (days)"])
        days_until_delivery = (delivery_date - today).days
        days_until_stockout = row["Current Stock (Qty)"] / row["Daily Avg Consumption"]
        if days_until_stockout < row["Buffer Stock (days)"] and days_until_delivery > days_until_stockout:
            return "High Risk 🔴"
        return "Low Risk 🟢"

    df["Inventory Risk"] = df.apply(compute_inventory_risk, axis=1)
    st.dataframe(df)
    st.bar_chart(df["Inventory Risk"].value_counts())

elif nav == "✏️ PO Entry Simulation":
    st.header("✏️ Simulate PO Risk Entry")
    df = load_supplier_data()
    supplier = st.selectbox("Select Supplier", df["Supplier"].unique())
    delay = st.slider("Expected Delay (days)", 0, 30, 5)
    reject = st.slider("Rejection Rate (%)", 0.0, 20.0, 5.0) / 100
    payment = st.slider("Payment Terms (days)", 15, 120, 45)
    stock = st.slider("Stock Buffer (days)", 0, 30, 10)
    location = st.slider("Location Risk Index (0–10)", 0, 10, 5)

    risk_score = 0
    if config["use_rejected_qty"] and reject > config["thresholds"]["rejection_rate"]:
        risk_score += 1
    if config["use_payment_terms"] and payment > config["thresholds"]["payment_terms_days"]:
        risk_score += 1
    if config["use_stock_buffer"] and stock < config["thresholds"]["min_stock_buffer_days"]:
        risk_score += 1
    if config["use_location_risk"] and location > config["thresholds"]["max_location_risk"]:
        risk_score += 1
    if delay > config["thresholds"]["delay_days"]:
        risk_score += 1

    sim_risk = "High Risk 🔴" if risk_score >= 3 else "Low Risk 🟢"
    st.success(f"Predicted Risk for {supplier}: **{sim_risk}**")

elif nav == "⚙️ Config Panel":
    st.header("⚙️ Configuration Settings")
    st.write("Update your risk thresholds and toggle parameters below.")

    config["use_rejected_qty"] = st.checkbox("Use Rejection Rate", config["use_rejected_qty"])
    config["use_payment_terms"] = st.checkbox("Use Payment Terms", config["use_payment_terms"])
    config["use_stock_buffer"] = st.checkbox("Use Stock Buffer", config["use_stock_buffer"])
    config["use_location_risk"] = st.checkbox("Use Location Risk Index", config["use_location_risk"])

    config["thresholds"]["delay_days"] = st.slider("Delay Threshold (days)", 0, 30, config["thresholds"]["delay_days"])
    config["thresholds"]["rejection_rate"] = st.slider("Rejection Rate Threshold", 0.0, 0.2, config["thresholds"]["rejection_rate"])
    config["thresholds"]["payment_terms_days"] = st.slider("Max Payment Terms", 15, 120, config["thresholds"]["payment_terms_days"])
    config["thresholds"]["min_stock_buffer_days"] = st.slider("Min Stock Buffer", 0, 30, config["thresholds"]["min_stock_buffer_days"])
    config["thresholds"]["max_location_risk"] = st.slider("Max Location Risk", 0, 10, config["thresholds"]["max_location_risk"])

    if st.button("💾 Save Configuration"):
        with open(config_path, "w") as f:
            json.dump(config, f, indent=4)
        st.success("Configuration saved!")
