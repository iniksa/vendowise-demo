import streamlit as st
import pandas as pd
import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import json
import os
from datetime import timedelta

sns.set_style("darkgrid")

# ---------------------------
# Config Management
# ---------------------------
config_path = "vendowise_config.json"
default_config = {
    "min_stock_buffer_days": 7,
    "delay_days": 5,
    "max_po_delay": 5,
    "max_location_risk": 6,
    "max_reject": 0.03,
    "max_payment_terms": 45
}

if not os.path.exists(config_path):
    config = default_config
    with open(config_path, "w") as f:
        json.dump(config, f, indent=4)

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
            st.stop()

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

    st.subheader("📉 Inventory Risk Classification Chart")
    risk_counts = inv_data["Buffer Breach Risk"].value_counts().rename({True: "High Risk", False: "Low Risk"})
    fig, ax = plt.subplots()
    sns.barplot(x=risk_counts.index, y=risk_counts.values, ax=ax)
    ax.set_ylabel("Number of Items")
    ax.set_title("Inventory Risk Classification")
    st.pyplot(fig)

# ---------------------------
# Vendor Dashboard with PO Simulation
# ---------------------------
def vendor_dashboard(vendor_data):
    tab1, tab2 = st.tabs(["📈 Vendor Performance", "🧮 Vendor PO Risk Simulation"])
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
        st.markdown("## ✏️ Vendor PO Risk Simulation")
        supplier = st.selectbox("Select Supplier", vendor_data["vendor_name"].unique())
        delay = st.number_input("Expected Delay (days)", 0, 30, 5)
        reject = st.number_input("Expected Rejection Rate (%)", 0.0, 20.0, 1.0) / 100
        payment = st.number_input("Payment Terms (days)", 15, 120, 45)
        stock = st.number_input("Available Stock Buffer (days)", 0, 30, 10)
        location = st.slider("Location Risk Index (0–10)", 0, 10, 5)

        risk = "High Risk 🔴" if (
            delay > config["max_po_delay"] or
            reject > config["max_reject"] or
            payment > config["max_payment_terms"] or
            stock < config["min_stock_buffer_days"] or
            location > config["max_location_risk"]
        ) else "Low Risk 🟢"
st.success("Settings saved successfully.")

# ---------------------------
# Main App
# ---------------------------
def main():
    st.set_page_config(page_title="VendoWise", layout="wide")

    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    if not st.session_state["logged_in"]:
        login()
        st.stop()

    # Sidebar Logo
    try:
        st.sidebar.image("Iniksa-TM.png", width=150)
    except:
        st.sidebar.markdown("**VendoWise**")

    st.sidebar.title("Supplier Risk Intelligence Hub")

    st.sidebar.header("Threshold Configuration")
with st.sidebar.expander("🔧 Threshold Configuration", expanded=False):
    min_stock_buffer = st.slider("Min Stock Buffer (Days)", 0, 30, 7)
    max_delivery_delay = st.slider("Max Acceptable Delivery Delay (Days)", 0, 15, 5)
    max_po_delay = st.slider("Max PO Delay", 0, 30, 5)
    max_location_risk = st.slider("Max Location Risk Score", 0, 10, 6)
    max_rejection_rate = st.slider("Max Rejection Rate (%)", 0.0, 20.0, 3.0)
    max_payment_terms = st.slider("Max Payment Terms (Days)", 15, 120, 45)

with st.sidebar.expander("📥 Data Input Mode", expanded=False):
    data_input_mode = st.radio("Choose data input mode", ["Sample Data", "Upload Your File"], index=0)
    st.button("Save Settings")

with open(config_path, "w") as f:
    json.dump(config, f, indent=4)
st.success("Settings saved successfully.")


if st.session_state.get("logged_in"):
    st.sidebar.title("Navigation")
    choice = st.sidebar.radio("Go to", ["Inventory Dashboard", "Vendor Dashboard", "Logout"])

# Load data
    if data_input_mode == "Sample Data":
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
