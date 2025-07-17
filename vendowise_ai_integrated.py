
import streamlit as st
import pandas as pd
import joblib

# --- Password Protection ---
def check_password():
    def password_entered():
        if st.session_state["password"] == "vendowise123":
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("Password", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("Password", type="password", on_change=password_entered, key="password")
        st.error("😕 Incorrect password")
        return False
    else:
        return True

if not check_password():
    st.stop()

# --- Branding ---
st.set_page_config(page_title="VendoWise", layout="wide")
st.sidebar.image("Iniksa-TM.png", use_container_width=True)
st.sidebar.markdown("### Your Supplier Risk Intelligence Hub")

# --- Load ML Model ---
@st.cache_resource
def load_model():
    return joblib.load("mock_supplier_risk_model.pkl")

model = load_model()

# --- Page Selection ---
page = st.sidebar.radio("Go to", ["Dashboard", "Configuration Panel"])

# --- Dashboard ---
if page == "Dashboard":
    st.title("📊 VendoWise Supplier Risk Dashboard")

    if "data" in st.session_state:
        df = st.session_state.data

        st.subheader("📌 Supplier Summary")
        st.dataframe(df.style.highlight_max(axis=0), use_container_width=True)

        st.subheader("📉 Charts")
        col1, col2 = st.columns(2)
        with col1:
            st.bar_chart(df.set_index("Supplier")["Avg_Delay_Days"])
        with col2:
            st.bar_chart(df.set_index("Supplier")["Rejection_Rate"])

        # --- Live Forecast from Dropdown ---
        st.markdown("### 🔮 Live Risk Forecast by Supplier")
        selected = st.selectbox("Choose Supplier", df["Supplier"].unique())
        selected_row = df[df["Supplier"] == selected].iloc[0]
        features = [[
            selected_row["Avg_Delay_Days"],
            selected_row["Rejection_Rate"],
            selected_row["Historical_Orders"],
            2.5  # Placeholder for lead time variance
        ]]
        prediction = model.predict(features)[0]
        prob = model.predict_proba(features)[0][prediction]

        if prediction == 1:
            st.error(f"⚠️ Predicted High Risk Supplier ({selected}) – Confidence: {prob:.2f}")
        else:
            st.success(f"✅ Predicted Low Risk Supplier ({selected}) – Confidence: {prob:.2f}")

        st.caption("Risk calculated based on delay, rejection, volume, and lead-time variance.")

        # --- Manual Input Popup ---
        st.markdown("---")
        st.markdown("### 🧠 Run Manual AI Risk Prediction")
        with st.expander("Enter Supplier Performance to Predict Risk:"):
            c1, c2 = st.columns(2)
            delay = c1.number_input("Average Delay Days", value=3.0, min_value=0.0)
            rejection = c2.number_input("Rejection Rate (%)", value=2.0, min_value=0.0, max_value=100.0) / 100

            c3, c4 = st.columns(2)
            volume = c3.number_input("Order Volume (Monthly)", value=100, min_value=1)
            variance = c4.slider("Lead Time Variance", 0.0, 10.0, 2.5)

            if st.button("🔍 Predict Now"):
                features = [[delay, rejection, volume, variance]]
                pred = model.predict(features)[0]
                proba = model.predict_proba(features)[0][pred]

                if pred == 1:
                    st.error(f"⚠️ High Risk Detected – Confidence: {proba:.2f}")
                else:
                    st.success(f"✅ Low Risk – Confidence: {proba:.2f}")

    else:
        st.warning("Please upload and configure supplier data from the Configuration Panel.")

# --- Configuration Panel ---
elif page == "Configuration Panel":
    st.title("⚙️ Configuration Panel")
    st.write("Upload your JDE-style PO data (.csv format):")

    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    if uploaded_file:
        try:
            jde_data = pd.read_csv(uploaded_file, parse_dates=["Order_Date", "Promised_Date", "Received_Date"])
            required = {"Supplier", "PO_Number", "Order_Date", "Promised_Date", "Received_Date", "Qty_Ordered", "Qty_Rejected"}
            if required.issubset(set(jde_data.columns)):
                df = jde_data.copy()
                df["Avg_Delay_Days"] = (df["Received_Date"] - df["Promised_Date"]).dt.days
                df["Rejection_Rate"] = df["Qty_Rejected"] / df["Qty_Ordered"]

                agg = df.groupby("Supplier").agg({
                    "Avg_Delay_Days": "mean",
                    "Rejection_Rate": "mean",
                    "PO_Number": "count"
                }).reset_index()
                agg.rename(columns={"PO_Number": "Historical_Orders"}, inplace=True)

                st.session_state.data = agg
                st.success("✅ Data uploaded and processed successfully.")
            else:
                st.error("Missing columns. Please use the required format.")
        except Exception as e:
            st.error(f"Error: {e}")

    st.info("Required columns: Supplier, PO_Number, Order_Date, Promised_Date, Received_Date, Qty_Ordered, Qty_Rejected")
