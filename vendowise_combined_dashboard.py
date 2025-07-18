# vendowise_combined_dashboard.py
import streamlit as st
import pandas as pd
import json
import plotly.express as px

# ------------------ USER AUTH ------------------

def login():
    st.markdown("# 🔑 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username == "admin" and password == "vendowise123":
            st.session_state.logged_in = True
        else:
            st.error("Incorrect username or password")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login()
    st.stop()

# ------------------ UI SETUP ------------------

st.set_page_config(page_title="VendoWise Dashboard", layout="wide")
st.markdown("""
    <style>
    .sidebar .sidebar-content { background-color: #1E1E1E; }
    .stApp { background-color: #0e1117; color: white; }
    .css-1v0mbdj, .css-hxt7ib { color: white; }
    </style>
""", unsafe_allow_html=True)

# ------------------ LOAD CONFIG ------------------

CONFIG_PATH = "vendowise_config.json"
def load_config():
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)

def save_config(cfg):
    with open(CONFIG_PATH, "w") as f:
        json.dump(cfg, f, indent=4)

config = load_config()

# ------------------ SIDEBAR ------------------

st.sidebar.image("Iniksa-TM.png", width=140)
st.sidebar.header("🧭 Navigation")
view = st.sidebar.radio("Go to:", ["Supplier Risk", "Inventory Risk", "Configuration"])
data_mode = st.sidebar.radio("Choose input mode:", ["Sample Data", "Upload CSV"], index=0)

# ------------------ LOAD DATA ------------------

supplier_sample = pd.read_csv("vendor_data.csv")
inventory_sample = pd.read_csv("inventory_data.csv")

supplier_file = inventory_file = None
if data_mode == "Upload CSV":
    if view == "Supplier Risk":
        supplier_file = st.sidebar.file_uploader("Upload Supplier Data", type="csv")
    elif view == "Inventory Risk":
        inventory_file = st.sidebar.file_uploader("Upload Inventory Data", type="csv")

# ------------------ SUPPLIER RISK ------------------

def show_supplier_risk():
    st.markdown("## 📊 Supplier Risk Dashboard")
    df = pd.read_csv(supplier_file) if supplier_file else supplier_sample

    expected_cols = ["Supplier", "ordered_qty", "received_qty", "rejected_qty", "expected_delivery_date", "actual_delivery_date", "freight_cost", "payment_terms", "stock_buffer", "location_risk"]
    missing = [col for col in expected_cols if col not in df.columns]
    if missing:
        st.error(f"Missing column: {', '.join(missing)}")
        return

    df["delay"] = (pd.to_datetime(df["actual_delivery_date"]) - pd.to_datetime(df["expected_delivery_date"]))
    df["delay"] = df["delay"].dt.days.clip(lower=0)
    df["rejection"] = df["rejected_qty"] / df["ordered_qty"]

    def compute_risk(row):
        risk = 0
        thresholds = config["thresholds"]
        if config["use_rejected_qty"] and row["rejection"] > thresholds["rejection_rate"]: risk += 1
        if config["use_partial_delivery"] and row["received_qty"] < row["ordered_qty"]: risk += 1
        if config["use_payment_terms"] and row["payment_terms"] > thresholds["payment_terms_days"]: risk += 1
        if config["use_stock_buffer"] and row["stock_buffer"] < thresholds["min_stock_buffer_days"]: risk += 1
        if config["use_location_risk"] and row["location_risk"] > thresholds["max_location_risk"]: risk += 1
        if config["use_freight_cost"] and row["freight_cost"] > 10000: risk += 1
        if row["delay"] > thresholds["delay_days"]: risk += 1
        return "High" if risk >= 3 else "Low"

    df["Risk"] = df.apply(compute_risk, axis=1)
    fig = px.bar(df, x="Supplier", y="delay", color="Risk", title="Delay Days by Supplier")
    fig.update_layout(template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(df)

# ------------------ INVENTORY RISK ------------------

def show_inventory_risk():
    st.markdown("## 📦 Inventory Risk Dashboard")
    df = pd.read_csv(inventory_file) if inventory_file else inventory_sample
    if not all(col in df.columns for col in ["item", "current_stock", "avg_daily_usage"]):
        st.error("Missing 'item' or 'current_stock' column in data.")
        return
    df["days_left"] = df["current_stock"] / df["avg_daily_usage"]
    df["Inventory Risk"] = df["days_left"].apply(lambda x: "Critical" if x < 7 else ("Moderate" if x < 14 else "Safe"))
    fig = px.bar(df, x="item", y="days_left", color="Inventory Risk", title="Days of Stock Remaining")
    fig.update_layout(template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(df)

# ------------------ CONFIGURATION ------------------

def show_config():
    st.markdown("## ⚙️ Configuration Panel")
    st.json(config)
    if st.button("Reload Config"):
        st.experimental_rerun()

# ------------------ MAIN ------------------

if view == "Supplier Risk":
    show_supplier_risk()
elif view == "Inventory Risk":
    show_inventory_risk()
else:
    show_config()
