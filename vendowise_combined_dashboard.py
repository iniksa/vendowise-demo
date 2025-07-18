
import streamlit as st
import pandas as pd
import json
import plotly.express as px

# ---------------------- Configuration ----------------------
CONFIG_PATH = "vendowise_config.json"
DEFAULT_USER = "admin"
DEFAULT_PASS = "vendowise123"

# ---------------------- Load Configuration ----------------------
def load_config():
    try:
        with open(CONFIG_PATH) as f:
            return json.load(f)
    except:
        return {}

def save_config(cfg):
    with open(CONFIG_PATH, "w") as f:
        json.dump(cfg, f, indent=4)

config = load_config()

# ---------------------- Login ----------------------
def login():
    st.sidebar.image("https://i.ibb.co/jT4D1t2/iniksa-logo-dark.png", width=150)
    st.sidebar.title("🧭 Navigation")
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        st.title("🔐 Login")
        user = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if user == DEFAULT_USER and password == DEFAULT_PASS:
                st.session_state.logged_in = True
            else:
                st.error("Invalid credentials")
        st.stop()

login()

# ---------------------- Sidebar ----------------------
page = st.sidebar.radio("Go to:", ["Supplier Risk", "Inventory Risk", "Configuration"])
input_mode = st.sidebar.radio("Choose input mode:", ["Sample Data", "Upload CSV"])

# ---------------------- Data Loaders ----------------------
def load_vendor_data():
    if input_mode == "Upload CSV":
        uploaded = st.sidebar.file_uploader("Upload Vendor CSV", type="csv", key="vendor")
        if uploaded:
            return pd.read_csv(uploaded)
        else:
            st.warning("Please upload vendor_data.csv file")
            st.stop()
    else:
        return pd.read_csv("vendor_data.csv")

def load_inventory_data():
    if input_mode == "Upload CSV":
        uploaded = st.sidebar.file_uploader("Upload Inventory CSV", type="csv", key="inventory")
        if uploaded:
            return pd.read_csv(uploaded)
        else:
            st.warning("Please upload inventory_data.csv file")
            st.stop()
    else:
        return pd.read_csv("inventory_data.csv")

# ---------------------- Supplier Risk ----------------------
if page == "Supplier Risk":
    st.title("📊 Supplier Risk Dashboard")
    df = load_vendor_data()

    required = ["Supplier", "ordered_qty", "received_qty", "rejected_qty", "expected_delivery_date"]
    for col in required:
        if col not in df.columns:
            st.error(f"Missing column: {col}")
            st.stop()

    # Apply risk logic
    df["Delay (days)"] = pd.to_datetime(df["expected_delivery_date"]) - pd.Timestamp.now()
    df["Delay (days)"] = df["Delay (days)"].dt.days
    df["Rejection Rate"] = df["rejected_qty"] / df["ordered_qty"]

    def classify(row):
        if config.get("use_rejected_qty", True) and row["Rejection Rate"] > config["thresholds"]["rejection_rate"]:
            return "High"
        if config.get("use_partial_delivery", False) and row["received_qty"] < row["ordered_qty"]:
            return "High"
        if row["Delay (days)"] > config["thresholds"]["delay_days"]:
            return "High"
        return "Low"

    df["Risk"] = df.apply(classify, axis=1)

    fig = px.bar(df, x="Supplier", y="Delay (days)", color="Risk", title="Supplier Risk Forecast")
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(df)

# ---------------------- Inventory Risk ----------------------
elif page == "Inventory Risk":
    st.title("📦 Inventory Risk Dashboard")
    df = load_inventory_data()
    required = ["item", "current_stock", "daily_demand", "lead_time_days"]
    for col in required:
        if col not in df.columns:
            st.error(f"Missing '{col}' column in data.")
            st.stop()

    df["days_of_stock"] = df["current_stock"] / df["daily_demand"]
    df["risk"] = df["days_of_stock"] < df["lead_time_days"]

    fig = px.bar(df, x="item", y="days_of_stock", color="risk", title="Inventory Buffer Forecast")
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(df)

# ---------------------- Config Panel ----------------------
else:
    st.title("⚙️ Configuration Panel")
    st.json(config)
    if st.button("🔄 Reload Config"):
        st.rerun()
