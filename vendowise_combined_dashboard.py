
import streamlit as st
import pandas as pd
import json
import os

import matplotlib.pyplot as plt
import seaborn as sns
import plotly.io as pio
pio.templates.default = "plotly_dark"
sns.set_style("darkgrid")


st.set_page_config(layout="wide")

# -------------------------
# 🔐 Login Logic
# -------------------------
def check_password():
    def password_entered():
        if st.session_state["username"] == "admin" and st.session_state["password"] == "vendowise123":
            st.session_state["password_correct"] = True
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("Username", key="username")
        st.text_input("Password", type="password", key="password", on_change=password_entered)
        st.stop()
    elif not st.session_state["password_correct"]:
        st.text_input("Username", key="username")
        st.text_input("Password", type="password", key="password", on_change=password_entered)
        st.error("❌ Incorrect username or password")
        st.stop()

check_password()

# -------------------------
# 📁 Sidebar Navigation
# -------------------------
with st.sidebar:
    st.image("Iniksa-TM.png", width=150)
    st.markdown("### 🧭 Navigation")
    nav = st.radio("Go to:", ["Supplier Risk", "Inventory Risk", "Configuration"])

    st.markdown("---")
    st.markdown("### 📂 Data Input")
    input_mode = st.radio("Choose input mode:", ["Sample Data", "Upload CSV"])

# -------------------------
# 📊 Supplier Risk Dashboard
# -------------------------
if nav == "Supplier Risk":
    st.title("📊 Supplier Risk Dashboard")
    if input_mode == "Upload CSV":
        uploaded_file = st.file_uploader("Upload Supplier Data CSV", type=["csv"])
        if uploaded_file:
            df = pd.read_csv(uploaded_file)
        else:
            st.warning("Please upload a CSV file.")
            st.stop()
    else:
        df = pd.read_csv("vendor_data.csv")

    expected_columns = [
        "Supplier", "ordered_qty", "received_qty", "rejected_qty", "expected_delivery_date"
    ]
    for col in expected_columns:
        if col not in df.columns:
            st.error(f"Missing column: {col}")
            st.stop()

    st.dataframe(df)

# -------------------------
# 📦 Inventory Risk Dashboard
# -------------------------
elif nav == "Inventory Risk":
    st.title("📦 Inventory Risk Dashboard")
    if input_mode == "Upload CSV":
        uploaded_file = st.file_uploader("Upload Inventory Data CSV", type=["csv"])
        if uploaded_file:
            df = pd.read_csv(uploaded_file)
        else:
            st.warning("Please upload a CSV file.")
            st.stop()
    else:
        df = pd.read_csv("inventory_data.csv")

    if "item" not in df.columns or "current_stock" not in df.columns:
        st.error("Missing 'item' or 'current_stock' column in data.")
        st.stop()

    st.dataframe(df)

# -------------------------
# ⚙️ Configuration Panel
# -------------------------
elif nav == "Configuration":
    st.title("⚙️ Configuration Panel")
    config_path = "vendowise_config.json"

    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            config = json.load(f)
    else:
        config = {}

    st.json(config)

    if st.button("🔄 Reload Config"):
        st.experimental_rerun()
