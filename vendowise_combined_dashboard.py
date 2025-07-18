
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# 🔒 Simple login
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

st.set_page_config(page_title="VendoWise Unified Dashboard", layout="wide")
st.title("📊 VendoWise Unified Risk Dashboard")

# Load data functions
@st.cache_data
def load_supplier_data():
    return pd.read_csv("vendor_data.csv")

@st.cache_data
def load_inventory_data():
    return pd.read_csv("inventory_data.csv")

# Tabs for unified dashboard
tab1, tab2 = st.tabs(["🚚 Supplier Risk", "📦 Inventory Forecast"])

# ----- SUPPLIER RISK -----
with tab1:
    st.subheader("🚚 Supplier Risk Panel")
    df = load_supplier_data()
    df["Expected Delay (days)"] = pd.to_numeric(df["Expected Delay (days)"], errors="coerce")
    df["Rejection Rate"] = pd.to_numeric(df["Rejection Rate"], errors="coerce")
    df["Payment Terms"] = pd.to_numeric(df["Payment Terms"], errors="coerce")
    df["Stock Buffer (days)"] = pd.to_numeric(df["Stock Buffer (days)"], errors="coerce")
    df["Location Risk Index"] = pd.to_numeric(df["Location Risk Index"], errors="coerce")

    # Configuration
    max_delay = st.slider("🔧 Max Delay Threshold (days)", 0, 15, 5, key="delay")
    max_reject = st.slider("🔧 Max Rejection Rate", 0.0, 0.2, 0.05, 0.01, key="reject")
    max_payment = st.slider("🔧 Max Payment Terms", 0, 120, 60, key="payment")
    min_buffer = st.slider("🔧 Min Stock Buffer", 0, 30, 10, key="buffer")
    max_loc_risk = st.slider("🔧 Max Location Risk Index", 0, 10, 6, key="locrisk")

    def supplier_risk(row):
        return "High Risk 🔴" if (
            row["Expected Delay (days)"] > max_delay or
            row["Rejection Rate"] > max_reject or
            row["Payment Terms"] > max_payment or
            row["Stock Buffer (days)"] < min_buffer or
            row["Location Risk Index"] > max_loc_risk
        ) else "Low Risk 🟢"

    df["Risk Status"] = df.apply(supplier_risk, axis=1)
    st.dataframe(df)

    risk_summary = df["Risk Status"].value_counts()
    fig1, ax1 = plt.subplots()
    risk_summary.plot(kind='bar', color=["red", "green"], ax=ax1)
    ax1.set_title("Supplier Risk Summary")
    st.pyplot(fig1)

# ----- INVENTORY RISK -----
with tab2:
    st.subheader("📦 Inventory Buffer Risk Forecast")
    df2 = load_inventory_data()
    df2["Next PO Delivery Date"] = pd.to_datetime(df2["Next PO Delivery Date"], errors="coerce")
    today = datetime(2025, 7, 17)

    def inventory_risk(row):
        if pd.isna(row["Next PO Delivery Date"]):
            return "No PO ❓"
        delivery_date = row["Next PO Delivery Date"] + timedelta(days=row["Expected Delay (days)"])
        days_until_delivery = (delivery_date - today).days
        days_until_stockout = row["Current Stock (Qty)"] / row["Daily Avg Consumption"]
        buffer_threshold = row["Buffer Stock (days)"]
        if days_until_stockout < buffer_threshold and days_until_delivery > days_until_stockout:
            return "High Risk 🔴"
        else:
            return "Low Risk 🟢"

    df2["Risk Status"] = df2.apply(inventory_risk, axis=1)
    st.dataframe(df2)

    inventory_summary = df2["Risk Status"].value_counts()
    fig2, ax2 = plt.subplots()
    inventory_summary.plot(kind='bar', color=["red", "green", "gray"], ax=ax2)
    ax2.set_title("Inventory Risk Classification")
    st.pyplot(fig2)
