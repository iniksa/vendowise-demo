
import streamlit as st
import pandas as pd
import json
import os
import matplotlib.pyplot as plt
import seaborn as sns

# ----------------- PASSWORD PROTECTION -----------------
def check_password():
    def password_entered():
        if st.session_state["password"] == "vendowise123":
            st.session_state["password_correct"] = True
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("Enter password", type="password", on_change=password_entered, key="password")
        st.stop()
    elif not st.session_state["password_correct"]:
        st.text_input("Enter password", type="password", on_change=password_entered, key="password")
        st.error("😕 Password incorrect")
        st.stop()

check_password()
# -------------------------------------------------------


# Load default config or from file
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
config_file = "vendowise_config.json"
if os.path.exists(config_file):
    with open(config_file, "r") as f:
        config = json.load(f)
else:
    config = default_config

# Sidebar - Configurable options
st.sidebar.header("Risk Factors Configuration")
config["use_rejected_qty"] = st.sidebar.checkbox("Include Rejection Rate", config["use_rejected_qty"])
config["use_freight_cost"] = st.sidebar.checkbox("Include Freight Cost", config["use_freight_cost"])
config["use_payment_terms"] = st.sidebar.checkbox("Include Payment Terms", config["use_payment_terms"])
config["use_stock_buffer"] = st.sidebar.checkbox("Include Stock Buffer", config["use_stock_buffer"])
config["use_location_risk"] = st.sidebar.checkbox("Include Location Risk", config["use_location_risk"])
config["use_partial_delivery"] = st.sidebar.checkbox("Include Partial Delivery", config["use_partial_delivery"])

# Thresholds
st.sidebar.subheader("Set Thresholds")
config["thresholds"]["delay_days"] = st.sidebar.slider("Max Delay Days", 0, 30, config["thresholds"]["delay_days"])
config["thresholds"]["rejection_rate"] = st.sidebar.slider("Max Rejection Rate", 0.0, 0.2, config["thresholds"]["rejection_rate"])
config["thresholds"]["payment_terms_days"] = st.sidebar.slider("Max Payment Terms (days)", 15, 120, config["thresholds"]["payment_terms_days"])
config["thresholds"]["min_stock_buffer_days"] = st.sidebar.slider("Min Stock Buffer (days)", 0, 30, config["thresholds"]["min_stock_buffer_days"])
config["thresholds"]["max_location_risk"] = st.sidebar.slider("Max Location Risk", 0, 10, config["thresholds"]["max_location_risk"])

# Save config button
if st.sidebar.button("💾 Save Configuration"):
    with open(config_file, "w") as f:
        json.dump(config, f, indent=4)
    st.sidebar.success("Configuration saved!")

# Main view
st.title("📊 VendoWise Supplier Risk Evaluator")

# Upload vendor data
uploaded_file = st.file_uploader("Upload vendor_data.csv", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.write("Uploaded Data Preview", df.head())

    def calculate_flags(row):
        delay = (pd.to_datetime(row["actual_delivery_date"]) - pd.to_datetime(row["expected_delivery_date"])).days
        flags = []
        if delay > config["thresholds"]["delay_days"]:
            flags.append("Delay")
        if config["use_rejected_qty"]:
            rejection = row["rejected_qty"] / row["received_qty"] if row["received_qty"] else 0
            if rejection > config["thresholds"]["rejection_rate"]:
                flags.append("Rejection")
        if config["use_payment_terms"] and row["payment_terms_days"] > config["thresholds"]["payment_terms_days"]:
            flags.append("Payment Terms")
        if config["use_stock_buffer"] and row["stock_buffer_days"] < config["thresholds"]["min_stock_buffer_days"]:
            flags.append("Low Stock Buffer")
        if config["use_location_risk"] and row["location_risk"] > config["thresholds"]["max_location_risk"]:
            flags.append("Location Risk")
        if config["use_partial_delivery"] and row["received_qty"] < row["ordered_qty"]:
            flags.append("Partial Delivery")
        return flags

    df["Risk Reasons"] = df.apply(calculate_flags, axis=1)
    df["Risk Level"] = df["Risk Reasons"].apply(lambda x: "High Risk 🔴 (" + ", ".join(x) + ")" if x else "Low Risk 🟢")
    st.dataframe(df)

    # Risk summary chart
    st.subheader("📈 Risk Summary Chart")
    all_flags = df["Risk Reasons"].explode().dropna()
    if not all_flags.empty:
        chart_data = all_flags.value_counts()
        fig, ax = plt.subplots()
        sns.barplot(x=chart_data.index, y=chart_data.values, ax=ax)
        ax.set_ylabel("Count")
        ax.set_xlabel("Risk Reason")
        ax.set_title("Frequency of Risk Reasons")
        plt.xticks(rotation=45)
        st.pyplot(fig)
