
import streamlit as st
import pandas as pd
import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import json
import os
from datetime import timedelta

# ---------------------------
# Load or Initialize Config
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

with open(config_path, "r") as f:
    config = json.load(f)

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
# Inventory Risk Dashboard
# ---------------------------
def inventory_dashboard(inventory_data):
    st.title("📦 Inventory Risk Dashboard")

    inventory_data["Next PO Delivery Date"] = pd.to_datetime(inventory_data["Next PO Delivery Date"], errors="coerce")
    today = pd.Timestamp(datetime.date.today())

    inventory_data["Expected Days Left"] = inventory_data["Current Stock (Qty)"] / inventory_data["Daily Avg Consumption"]
    inventory_data["Buffer Breach Risk"] = inventory_data["Expected Days Left"] < config["min_stock_buffer_days"]
    inventory_data["Delay Impact"] = inventory_data["Expected Delay (days)"] > config["delay_days"]

    st.subheader("📊 Inventory Risk Summary")
    st.dataframe(inventory_data.style.applymap(
        lambda val: "background-color: red" if val is True else "",
        subset=["Buffer Breach Risk", "Delay Impact"]
    ))

    st.subheader("🧮 Simulate PO Risk")
    item_code = st.text_input("Item Code")
    stock_qty = st.number_input("Current Stock Qty", min_value=0)
    daily_usage = st.number_input("Daily Usage", min_value=1)
    buffer_days = st.number_input("Buffer Days", min_value=1, value=config["min_stock_buffer_days"])
    po_delay = st.number_input("Expected Delay (Days)", min_value=0)
    po_date = st.date_input("PO Date", min_value=today.date())

    if st.button("Check Risk"):
        days_until_delivery = (pd.Timestamp(po_date) + timedelta(days=po_delay) - today).days
        days_until_stockout = stock_qty / daily_usage
        if days_until_stockout < buffer_days and days_until_delivery > days_until_stockout:
            risk = "High Risk 🔴"
        else:
            risk = "Low Risk 🟢"
        st.success(f"Predicted Risk for {item_code}: **{risk}**")

# ---------------------------
# Vendor Risk Dashboard
# ---------------------------
def vendor_dashboard(vendor_data):
    st.title("🤝 Vendor Risk Dashboard")

    vendor_data["expected_delivery_date"] = pd.to_datetime(vendor_data["expected_delivery_date"], errors="coerce")
    vendor_data["actual_delivery_date"] = pd.to_datetime(vendor_data["actual_delivery_date"], errors="coerce")
    vendor_data["delivery_delay"] = (vendor_data["actual_delivery_date"] - vendor_data["expected_delivery_date"]).dt.days
    vendor_data["on_time"] = vendor_data["delivery_delay"] <= config["max_po_delay"]

    st.subheader("🚚 Vendor Delivery Performance")
    st.dataframe(vendor_data.style.applymap(
        lambda val: "background-color: red" if val is False else "",
        subset=["on_time"]
    ))

    st.subheader("📦 Rejection Rate & Freight")
    vendor_data["rejection_rate (%)"] = (vendor_data["rejected_qty"] / vendor_data["ordered_qty"]) * 100
    st.dataframe(vendor_data[["vendor_name", "item_code", "rejection_rate (%)", "freight_cost", "location_risk"]]
                 .style.applymap(
                     lambda val: "background-color: orange" if isinstance(val, (int, float)) and val > config["max_location_risk"]
                     else ""
                 , subset=["location_risk"]))

    st.subheader("📈 Rejection Rate Chart")
    fig, ax = plt.subplots(figsize=(8, 4))
    sns.barplot(x="vendor_name", y="rejection_rate (%)", data=vendor_data, ax=ax)
    plt.xticks(rotation=45)
    st.pyplot(fig)

# ---------------------------
# Main App Routing
# ---------------------------
def main():
    st.set_page_config(page_title="VendoWise Dashboard", layout="wide")

    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    if not st.session_state["logged_in"]:
        login()
    else:
        st.sidebar.title("📂 Navigation")
        choice = st.sidebar.radio("Go to", ["Inventory Dashboard", "Vendor Dashboard", "Save Settings", "Logout"])

        # Configuration sidebar
        st.sidebar.title("⚙️ Configuration")
        config["min_stock_buffer_days"] = st.sidebar.number_input("Minimum Stock Buffer (Days)", value=config["min_stock_buffer_days"])
        config["delay_days"] = st.sidebar.number_input("Acceptable Delivery Delay (Days)", value=config["delay_days"])
        config["max_po_delay"] = st.sidebar.slider("Max Acceptable PO Delay", 0, 30, value=config["max_po_delay"])
        config["max_location_risk"] = st.sidebar.slider("Max Location Risk Score", 0, 10, value=config["max_location_risk"])

        # Uploads
        st.sidebar.title("📁 Upload Data")
        inventory_file = st.sidebar.file_uploader("Upload Inventory CSV", type=["csv"])
        vendor_file = st.sidebar.file_uploader("Upload Vendor CSV", type=["csv"])

        if choice == "Inventory Dashboard" and inventory_file:
            inv_data = pd.read_csv(inventory_file)
            inventory_dashboard(inv_data)

        elif choice == "Vendor Dashboard" and vendor_file:
            ven_data = pd.read_csv(vendor_file)
            vendor_dashboard(ven_data)

        elif choice == "Save Settings":
            with open(config_path, "w") as f:
                json.dump(config, f, indent=4)
            st.success("Settings saved successfully.")

        elif choice == "Logout":
            st.session_state["logged_in"] = False
            st.experimental_rerun()

if __name__ == "__main__":
    main()
