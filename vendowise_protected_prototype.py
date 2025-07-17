# Recreate the corrected and complete Streamlit app file with properly closed markdown styling block

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Basic password protection
def check_password():
    def password_entered():
        if st.session_state["password"] == "vendowise123":
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("Enter password", type="password", on_change=password_entered, key="password")
        st.stop()
    elif not st.session_state["password_correct"]:
        st.text_input("Enter password", type="password", on_change=password_entered, key="password")
        st.error("😕 Incorrect password")
        st.stop()

check_password()

st.set_page_config(page_title="VendoWise - Supplier Risk Command Center", layout="wide")

# Custom Dark Theme Styling
st.markdown('''
<style>
html, body, [class*="css"]  {
    font-family: 'Segoe UI', sans-serif;
}
.main {
    background-color: #0e1117;
    color: #ffffff;
}
.st-bb, .st-at {
    background-color: #262730;
    color: #ffffff;
}
.stButton>button {
    background-color: #1985a1;
    color: white;
    font-weight: bold;
}
.block-container {
    padding: 2rem 2rem;
}
</style>
''', unsafe_allow_html=True)

# Logo & Branding
st.sidebar.image("Iniksa-TM.png", use_container_width=True)
st.sidebar.markdown("**Your Supplier Risk Intelligence Hub**", unsafe_allow_html=True)
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Dashboard", "PO Entry Simulation", "Configuration Panel"])

# Load default sample data
default_data = pd.DataFrame({
    'Supplier': ['Alpha', 'Bravo', 'Charlie', 'Delta', 'Echo'],
    'Avg_Delay_Days': [2, 7, 4, 10, 1],
    'Rejection_Rate': [0.02, 0.07, 0.04, 0.10, 0.01],
    'Historical_Orders': [50, 75, 40, 60, 55]
})

# Threshold settings
st.sidebar.markdown("---")
st.sidebar.header("Alert Thresholds")
delay_threshold = st.sidebar.slider("Max acceptable delay (days)", 0, 15, 5)
rejection_threshold = st.sidebar.slider("Max rejection rate (%)", 0, 20, 5) / 100

# Main session data
if "data" not in st.session_state:
    st.session_state.data = default_data

# Header
st.markdown("## 🧠 VendoWise: Supplier Risk Intelligence System")
st.caption("Gain real-time insights into supplier delays and quality issues.")

# Dashboard Page
if page == "Dashboard":
    st.header("📊 Supplier Risk Dashboard")
    df = st.session_state.data.copy()
    df["Delay_Flag"] = df["Avg_Delay_Days"] > delay_threshold
    df["Rejection_Flag"] = df["Rejection_Rate"] > rejection_threshold
    df["Risk_Score"] = df["Delay_Flag"].astype(int)*0.5 + df["Rejection_Flag"].astype(int)*0.5

    st.dataframe(df[["Supplier", "Avg_Delay_Days", "Rejection_Rate", "Risk_Score"]], use_container_width=True)

    st.subheader("📈 Average Delay by Supplier")
    fig1, ax1 = plt.subplots()
    ax1.bar(df["Supplier"], df["Avg_Delay_Days"], color="#1985a1")
    ax1.axhline(delay_threshold, color="red", linestyle="--", label="Threshold")
    ax1.set_ylabel("Avg Delay Days")
    ax1.set_title("Average Delay")
    ax1.legend()
    st.pyplot(fig1)

    st.subheader("📉 Rejection Rate by Supplier")
    fig2, ax2 = plt.subplots()
    ax2.bar(df["Supplier"], df["Rejection_Rate"] * 100, color="#6c5ce7")
    ax2.axhline(rejection_threshold * 100, color="red", linestyle="--", label="Threshold")
    ax2.set_ylabel("Rejection Rate (%)")
    ax2.set_title("Rejection Rate")
    ax2.legend()
    st.pyplot(fig2)

    st.subheader("🚨 High Risk Suppliers")
    high_risk = df[df["Risk_Score"] > 0.6]
    if not high_risk.empty:
        st.table(high_risk[["Supplier", "Risk_Score"]])
    else:
        st.success("All suppliers are currently within acceptable risk thresholds.")

# PO Entry Simulation Page
elif page == "PO Entry Simulation":
    st.header("📝 PO Entry Simulation")
    df = st.session_state.data
    supplier = st.selectbox("Select Supplier", df["Supplier"].unique())
    st.write(f"Checking supplier risk for: **{supplier}**")

    selected = df[df["Supplier"] == supplier].iloc[0]
    delay_flag = selected["Avg_Delay_Days"] > delay_threshold
    rejection_flag = selected["Rejection_Rate"] > rejection_threshold
    score = (0.5 if delay_flag else 0) + (0.5 if rejection_flag else 0)

    st.metric("Average Delay (days)", selected["Avg_Delay_Days"])
    st.metric("Rejection Rate (%)", f"{selected['Rejection_Rate']*100:.1f}%")
    st.metric("Risk Score", score)

    if score > 0.6:
        st.error("⚠️ High risk supplier. Consider alternate vendors.")
    elif score > 0:
        st.warning("⚠️ Medium risk supplier. Monitor carefully.")
    else:
        st.success("✅ Low risk supplier. Safe to proceed.")

# Configuration Panel Page
elif page == "Configuration Panel":
    st.header("⚙️ Configuration Panel")
    st.write("Upload your custom JDE-style PO data (.csv format):")

    uploaded_file = st.file_uploader("Choose JDE PO CSV", type="csv")
    if uploaded_file:
        try:
            jde_data = pd.read_csv(uploaded_file, parse_dates=["Order_Date", "Promised_Date", "Received_Date"])
            required_cols = {"Supplier", "PO_Number", "Order_Date", "Promised_Date", "Received_Date", "Qty_Ordered", "Qty_Rejected"}
            if required_cols.issubset(set(jde_data.columns)):
                # Calculate metrics
                processed = jde_data.copy()
                processed["Avg_Delay_Days"] = (processed["Received_Date"] - processed["Promised_Date"]).dt.days
                processed["Rejection_Rate"] = processed["Qty_Rejected"] / processed["Qty_Ordered"]
                
                # Aggregate by Supplier
                agg_df = processed.groupby("Supplier").agg({
                    "Avg_Delay_Days": "mean",
                    "Rejection_Rate": "mean",
                    "PO_Number": "count"
                }).reset_index()
                agg_df.rename(columns={"PO_Number": "Historical_Orders"}, inplace=True)

                st.session_state.data = agg_df
                st.success("✅ JDE-style PO data loaded and converted successfully.")
            else:
                st.error("❌ Missing required columns. Please upload a valid JDE PO format.")
        except Exception as e:
            st.error(f"Error processing file: {e}")

    st.info("Required columns: Supplier, PO_Number, Order_Date, Promised_Date, Received_Date, Qty_Ordered, Qty_Rejected")

