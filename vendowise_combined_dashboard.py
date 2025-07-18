import streamlit as st
import pandas as pd
import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import json
import os
from datetime import timedelta

# Set Seaborn style
sns.set_style("darkgrid")

# ---------------------------
# Config Management
# ---------------------------
config_path = "vendowise_config.json"
default_config = {
    "min_stock_buffer_days": 7,
    "delay_days": 5,
    "max_po_delay": 5,
    "max_location_risk": 6
}

if not os.path.exists(config_path):
    with open(config_path, "w") as f:
        json.dump(default_config, f, indent=4)

try:
    with open(config_path, "r") as f:
        config = json.load(f)
        for key in default_config:
            if key not in config:
                config[key] = default_config[key]
except json.JSONDecodeError:
    config = default_config
    with open(config_path, "w") as f:
        json.dump(config, f, indent=4)

# ---------------------------
# Authentication
# ---------------------------
def login():
    st.title("🔐 VendoWise Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username == "admin" and password == "vendowise123":
            st.session_state["logged_in"] = True
        else:
            st.error("Invalid credentials")

# ---------------------------
# Load Sample Data
# ---------------------------
def load_sample_inventory():
    return pd.read_csv("inventory_data.csv")

def load_sample_vendor():
    return pd.read_csv("vendor_data.csv")

# ---------------------------
# Inventory Dashboard
# ---------------------------
def inventory_dashboard(inv_data):
    st.title("📦 Inventory Risk Dashboard")
    today = pd.Timestamp(datetime.date.today())
    inv_data["Next PO Delivery Date"] = pd.to_datetime(inv_data["Next PO Delivery Date"], errors="coerce")
    inv_data["Expected Days Left"] = inv_data["Current Stock (Qty)"] / inv_data["Daily Avg Consumption"]
    inv_data["Buffer Breach Risk"] = inv_data["Expected Days Left"] < config["min_stock_buffer_days"]
    inv_data["Delay Impact"] = inv_data["Expected Delay (days)"] > config["delay_days"]

    st.subheader("📊 Inventory Risk Summary")
    st.dataframe(inv_data.style.applymap(
        lambda val: "background-color: red" if val is True else "",
        subset=["Buffer Breach Risk", "Delay Impact"]
    ))

# ---------------------------
# Vendor Dashboard
# ---------------------------
def vendor_dashboard(vendor_data):
    tab1, tab2 = st.tabs(["📈 Vendor Performance", "🧮 PO Risk Simulation"])
    today = pd.Timestamp(datetime.date.today())

    with tab1:
        st.subheader("🚚 Vendor Delivery Performance")
        vendor_data["expected_delivery_date"] = pd.to_datetime(vendor_data["expected_delivery_date"], errors="coerce")
        vendor_data["actual_delivery_date"] = pd.to_datetime(vendor_data["actual_delivery_date"], errors="coerce")
        vendor_data["delivery_delay"] = (vendor_data["actual_delivery_date"] - vendor_data["expected_delivery_date"]).dt.days
        vendor_data["on_time"] = vendor_data["delivery_delay"] <= config["max_po_delay"]
        st.dataframe(vendor_data.style.applymap(
            lambda val: "background-color: red" if val is False else "",
            subset=["on_time"]
        ))

        st.subheader("📦 Rejection & Freight Overview")
        vendor_data["rejection_rate (%)"] = (vendor_data["rejected_qty"] / vendor_data["ordered_qty"]) * 100
        st.dataframe(vendor_data[["vendor_name", "item_code", "rejection_rate (%)", "freight_cost", "location_risk"]]
                     .style.applymap(
                         lambda val: "background-color: orange" if isinstance(val, (int, float)) and val > config["max_location_risk"]
                         else "", subset=["location_risk"]))

        st.subheader("📊 Rejection Rate Chart")
        fig, ax = plt.subplots(figsize=(8, 4))
        sns.barplot(x="vendor_name", y="rejection_rate (%)", data=vendor_data, ax=ax)
        plt.xticks(rotation=45)
        st.pyplot(fig)

    with tab2:
        st.subheader("🧮 PO Simulation")
        item_code = st.text_input("Item Code")
        stock_qty = st.number_input("Current Stock Qty", min_value=0)
        daily_usage = st.number_input("Daily Usage", min_value=1)
        buffer_days = st.number_input("Buffer Days", min_value=1, value=config["min_stock_buffer_days"])
        po_delay = st.number_input("Expected Delay (Days)", min_value=0)
        po_date = st.date_input("PO Date", min_value=today.date())

        if st.button("Check Risk"):
            days_until_delivery = (pd.Timestamp(po_date) + timedelta(days=po_delay) - today).days
            days_until_stockout = stock_qty / daily_usage
            risk = "High Risk 🔴" if days_until_stockout < buffer_days and days_until_delivery > days_until_stockout else "Low Risk 🟢"
            st.success(f"Predicted Risk for {item_code}: **{risk}**")

# ---------------------------
# Main App
# ---------------------------
def main():
    st.set_page_config(page_title="VendoWise", layout="wide")
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    if not st.session_state["logged_in"]:
        login()
    else:
        st.sidebar.title("⚙️ Configuration")
        config["min_stock_buffer_days"] = st.sidebar.number_input("Min Stock Buffer Days", value=config["min_stock_buffer_days"])
        config["delay_days"] = st.sidebar.number_input("Acceptable Delivery Delay (Days)", value=config["delay_days"])
        config["max_po_delay"] = st.sidebar.slider("Max PO Delay (Days)", 0, 30, value=config["max_po_delay"])
        config["max_location_risk"] = st.sidebar.slider("Max Location Risk Score", 0, 10, value=config["max_location_risk"])

        data_mode = st.sidebar.radio("Choose data input mode", ["Sample Data", "Upload Your File"])

        if st.sidebar.button("Save Settings"):
            with open(config_path, "w") as f:
                json.dump(config, f, indent=4)
            st.success("Settings saved successfully.")

        st.sidebar.title("📂 Navigation")
        choice = st.sidebar.radio("Go to", ["Inventory Dashboard", "Vendor Dashboard", "Logout"])

        # Load inventory
        if data_mode == "Sample Data":
            inventory_data = load_sample_inventory()
            vendor_data = load_sample_vendor()
        else:
            inv_file = st.sidebar.file_uploader("Upload Inventory CSV", type=["csv"])
            ven_file = st.sidebar.file_uploader("Upload Vendor CSV", type=["csv"])
            inventory_data = pd.read_csv(inv_file) if inv_file else None
            vendor_data = pd.read_csv(ven_file) if ven_file else None

        if choice == "Inventory Dashboard":
            if inventory_data is not None:
                inventory_dashboard(inventory_data)
            else:
                st.warning("Upload or select sample inventory data.")
        elif choice == "Vendor Dashboard":
            if vendor_data is not None:
                vendor_dashboard(vendor_data)
            else:
                st.warning("Upload or select sample vendor data.")
        elif choice == "Logout":
            st.session_state["logged_in"] = False
            st.experimental_rerun()

if __name__ == "__main__":
    main()

