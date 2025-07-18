
import streamlit as st
import pandas as pd
import json
import plotly.express as px

st.set_page_config(layout="wide", page_title="VendoWise Dashboard")

# ---------------------- Login ----------------------
def login():
    st.sidebar.image("Iniksa-TM.png", width=150)
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.title("🔐 Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if username == "admin" and password == "vendowise123":
                st.session_state.authenticated = True
            else:
                st.error("Invalid credentials")
        st.stop()

login()

# ---------------------- Sidebar ----------------------
st.sidebar.header("🧭 Navigation")
section = st.sidebar.radio("Go to:", ["Supplier Risk", "Inventory Risk", "Configuration"])
input_mode = st.sidebar.radio("Choose input mode:", ["Sample Data", "Upload CSV"])

# ---------------------- Config Handling ----------------------
config_file = "vendowise_config.json"
default_config = {
    "use_rejected_qty": True,
    "use_freight_cost": True,
    "use_payment_terms": True,
    "use_stock_buffer": True,
    "use_location_risk": True,
    "use_partial_delivery": False,
    "thresholds": {
        "delay_days": 5,
        "rejection_rate": 0.05,
        "payment_terms_days": 60,
        "min_stock_buffer_days": 7,
        "max_location_risk": 5
    }
}

def load_config():
    try:
        with open(config_file, "r") as f:
            return json.load(f)
    except:
        return default_config

config = load_config()

# ---------------------- Supplier Data ----------------------
def load_supplier_data():
    if input_mode == "Upload CSV":
        uploaded = st.sidebar.file_uploader("Upload vendor_data.csv", type="csv")
        if uploaded:
            df = pd.read_csv(uploaded)
        else:
            st.warning("Please upload vendor_data.csv")
            st.stop()
    else:
        df = pd.read_csv("vendor_data.csv")

    # Column mapping
    rename_map = {
        "vendor_name": "Supplier",
        "payment_terms_days": "Payment Terms",
        "stock_buffer_days": "Stock Buffer (days)",
        "location_risk": "Location Risk Index"
    }
    df = df.rename(columns=rename_map)

    expected = ["Supplier", "ordered_qty", "received_qty", "rejected_qty", "expected_delivery_date",
                "actual_delivery_date", "freight_cost", "Payment Terms", "Stock Buffer (days)", "Location Risk Index"]
    missing = [col for col in expected if col not in df.columns]
    if missing:
        st.error(f"Missing column(s): {', '.join(missing)}")
        st.stop()

    return df

# ---------------------- Inventory Data ----------------------
def load_inventory_data():
    if input_mode == "Upload CSV":
        uploaded = st.sidebar.file_uploader("Upload inventory_data.csv", type="csv")
        if uploaded:
            df = pd.read_csv(uploaded)
        else:
            st.warning("Please upload inventory_data.csv")
            st.stop()
    else:
        df = pd.read_csv("inventory_data.csv")

    df = df.rename(columns={
        "Item Code": "item",
        "Current Stock (Qty)": "current_stock",
        "Daily Avg Consumption": "daily_consumption",
        "Buffer Stock (days)": "buffer_days",
        "Expected Delay (days)": "expected_delay"
    })

    expected = ["item", "current_stock", "daily_consumption", "buffer_days", "expected_delay"]
    missing = [col for col in expected if col not in df.columns]
    if missing:
        st.error(f"Missing column(s): {', '.join(missing)}")
        st.stop()

    return df

# ---------------------- Supplier Risk ----------------------
if section == "Supplier Risk":
    st.title("📊 Supplier Risk Dashboard")
    df = load_supplier_data()

    delay = (pd.to_datetime(df["actual_delivery_date"]) - pd.to_datetime(df["expected_delivery_date"])).dt.days
    df["delay_days"] = delay.fillna(0)
    df["rejection_rate"] = df["rejected_qty"] / df["ordered_qty"]

    def assess(row):
        if (config["use_partial_delivery"] and row["received_qty"] < row["ordered_qty"]) or            (config["use_rejected_qty"] and row["rejection_rate"] > config["thresholds"]["rejection_rate"]) or            (config["use_freight_cost"] and row["freight_cost"] > 0) or            (config["use_payment_terms"] and row["Payment Terms"] > config["thresholds"]["payment_terms_days"]) or            (config["use_stock_buffer"] and row["Stock Buffer (days)"] < config["thresholds"]["min_stock_buffer_days"]) or            (config["use_location_risk"] and row["Location Risk Index"] > config["thresholds"]["max_location_risk"]) or            (row["delay_days"] > config["thresholds"]["delay_days"]):
            return "High Risk 🔴"
        return "Low Risk 🟢"

    df["risk"] = df.apply(assess, axis=1)

    fig = px.bar(df, x="Supplier", y="delay_days", color="risk", title="Supplier Delay vs Risk",
                 color_discrete_map={"High Risk 🔴": "#FF4B4B", "Low Risk 🟢": "#00C853"})
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(30,30,30,0.1)')
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(df)

# ---------------------- Inventory Risk ----------------------
elif section == "Inventory Risk":
    st.title("📦 Inventory Risk Dashboard")
    df = load_inventory_data()

    df["days_left"] = df["current_stock"] / df["daily_consumption"]
    df["risk"] = df["days_left"] < df["buffer_days"]

    fig = px.bar(df, x="item", y="days_left", color="risk", title="Inventory Buffer Forecast",
                 color_discrete_map={True: "#FF4B4B", False: "#00C853"})
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(30,30,30,0.1)')
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(df)

# ---------------------- Config Panel ----------------------
elif section == "Configuration":
    st.title("⚙️ Configuration Panel")
    st.json(config)
    if st.button("🔁 Reload Config"):
        st.cache_data.clear()
        st.experimental_rerun()

