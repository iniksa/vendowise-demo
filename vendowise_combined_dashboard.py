
import streamlit as st
import pandas as pd
import json

st.set_page_config(page_title="VendoWise Dashboard", layout="wide")

# Authentication
def check_login():
    password = st.sidebar.text_input("Enter password", type="password")
    if password != "admin":
        st.warning("Incorrect password. Try again.")
        st.stop()

check_login()

# Load config
def load_config():
    try:
        with open("vendowise_config.json", "r") as f:
            return json.load(f)
    except:
        return {
            "delay_threshold": 7,
            "rejection_threshold": 0.05,
            "payment_terms": 60,
            "stock_buffer_days": 10,
            "location_risk": 6
        }

config = load_config()

# Load data safely
def load_csv(filepath, expected_columns):
    try:
        df = pd.read_csv(filepath)
        missing = [col for col in expected_columns if col not in df.columns]
        if missing:
            st.warning(f"Missing columns in {filepath}: {', '.join(missing)}")
            return None
        return df
    except Exception as e:
        st.warning(f"Could not load {filepath}: {e}")
        return None

# Supplier Risk Tab
def supplier_risk_tab():
    st.title("📦 Supplier Risk Forecast")

    expected_cols = [
        "Supplier", "Expected Delay (days)", "Rejection Rate",
        "Payment Terms", "Stock Buffer (days)", "Location Risk Index"
    ]
    df = load_csv("vendor_data.csv", expected_cols)
    if df is None:
        return

    df["Expected Delay (days)"] = pd.to_numeric(df["Expected Delay (days)"], errors="coerce")
    df["Rejection Rate"] = pd.to_numeric(df["Rejection Rate"], errors="coerce")

    df["Risk"] = df.apply(lambda row: "High Risk 🔴" if (
        row["Expected Delay (days)"] > config["delay_threshold"] or
        row["Rejection Rate"] > config["rejection_threshold"] or
        row["Payment Terms"] > config["payment_terms"] or
        row["Stock Buffer (days)"] < config["stock_buffer_days"] or
        row["Location Risk Index"] > config["location_risk"]
    ) else "Low Risk 🟢", axis=1)

    st.dataframe(df)

    st.bar_chart(df.set_index("Supplier")[["Expected Delay (days)", "Rejection Rate"]])

# Inventory Buffer Tab
def inventory_risk_tab():
    st.title("📊 Inventory Buffer Forecast")

    expected_cols = [
        "Item", "Current Stock", "Avg Daily Usage", "Reorder Level"
    ]
    df = load_csv("inventory_data.csv", expected_cols)
    if df is None:
        return

    df["Buffer Days"] = df["Current Stock"] / df["Avg Daily Usage"]
    df["Risk"] = df.apply(lambda row: "Low Stock ❗" if row["Buffer Days"] < 7 else "Healthy ✅", axis=1)

    st.dataframe(df)
    st.bar_chart(df.set_index("Item")[["Buffer Days"]])

# PO Entry Simulation
def po_entry_tab():
    st.title("✏️ PO Entry Simulation")
    df = load_csv("vendor_data.csv", ["Supplier"])
    if df is None:
        return

    supplier = st.selectbox("Select Supplier", df["Supplier"].unique())
    delay = st.number_input("Expected Delay (days)", 0, 30, 5)
    reject = st.number_input("Expected Rejection Rate (%)", 0.0, 20.0, 1.0) / 100
    payment = st.number_input("Payment Terms (days)", 15, 120, 45)
    stock = st.number_input("Available Stock Buffer (days)", 0, 30, 10)
    location = st.slider("Location Risk Index (0–10)", 0, 10, 5)

    risk = "High Risk 🔴" if (
        delay > config["delay_threshold"] or
        reject > config["rejection_threshold"] or
        payment > config["payment_terms"] or
        stock < config["stock_buffer_days"] or
        location > config["location_risk"]
    ) else "Low Risk 🟢"

    st.success(f"Predicted Risk for {supplier}: **{risk}**")

# Sidebar Navigation
st.sidebar.title("🔎 Navigation")
page = st.sidebar.radio("Go to", ["Supplier Risk", "Inventory Forecast", "PO Entry Simulation"])

if page == "Supplier Risk":
    supplier_risk_tab()
elif page == "Inventory Forecast":
    inventory_risk_tab()
elif page == "PO Entry Simulation":
    po_entry_tab()
