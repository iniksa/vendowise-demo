import streamlit as st
import pandas as pd
import datetime

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
def inventory_dashboard(inventory_data, config):
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

# ---------------------------
# Vendor Risk Dashboard
# ---------------------------
def vendor_dashboard(vendor_data, config):
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
        choice = st.sidebar.radio("Go to", ["Inventory Dashboard", "Vendor Dashboard", "Logout"])

        # Configuration sections
        st.sidebar.title("⚙️ Configuration")

        st.sidebar.subheader("📦 Inventory Configuration")
        min_stock_buffer_days = st.sidebar.number_input("Minimum Stock Buffer (Days)", value=7)
        delay_days = st.sidebar.number_input("Acceptable Delivery Delay (Days)", value=5)

        st.sidebar.subheader("🤝 Vendor Configuration")
        max_po_delay = st.sidebar.slider("Max Acceptable PO Delay", 0, 30, value=5)
        max_location_risk = st.sidebar.slider("Max Location Risk Score", 0, 10, value=6)

        config = {
            "min_stock_buffer_days": min_stock_buffer_days,
            "delay_days": delay_days,
            "max_po_delay": max_po_delay,
            "max_location_risk": max_location_risk
        }

        if choice == "Logout":
            st.session_state["logged_in"] = False
            st.experimental_rerun()

        # File upload section
        st.sidebar.title("📁 Upload Data")
        inventory_file = st.sidebar.file_uploader("Upload Inventory CSV", type=["csv"])
        vendor_file = st.sidebar.file_uploader("Upload Vendor CSV", type=["csv"])

        if choice == "Inventory Dashboard" and inventory_file:
            inv_data = pd.read_csv(inventory_file)
            inventory_dashboard(inv_data, config)
        elif choice == "Vendor Dashboard" and vendor_file:
            ven_data = pd.read_csv(vendor_file)
            vendor_dashboard(ven_data, config)
        else:
            st.info("Please upload the relevant data file to proceed.")

if __name__ == "__main__":
    main()
