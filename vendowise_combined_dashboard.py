import streamlit as st
import pandas as pd
import json
import os

# ---- LOGIN ----
def login():
    st.markdown("## 🔐 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username == "admin" and password == "admin":
            st.session_state["authenticated"] = True
        else:
            st.error("❌ Invalid credentials")
            st.stop()

if "authenticated" not in st.session_state:
    login()

# ---- CONFIG LOAD ----
@st.cache_data
def load_config():
    with open("vendowise_config.json", "r") as f:
        return json.load(f)

config = load_config()

# ---- SIDEBAR NAVIGATION ----
st.sidebar.title("🧭 Navigation")
nav = st.sidebar.radio("Go to:", ["Supplier Risk", "Inventory Risk", "Configuration"])

# ---- APP BODY ----
if nav == "Supplier Risk":
    
    import streamlit as st
    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sns
    import json
    import os
    
    # ----------------- PASSWORD PROTECTION -----------------
    
    #def check_password():
    #    def password_entered():
    #        if st.session_state["password"] == "vendowise123":
    #            st.session_state["password_correct"] = True
    #        else:
    #            st.session_state["password_correct"] = False
    #
     #   if "password_correct" not in st.session_state:
     #       st.text_input("Enter password", type="password", on_change=password_entered, key="password")
     #       st.stop()
      #  elif not st.session_state["password_correct"]:
      #      st.text_input("Enter password", type="password", on_change=password_entered, key="password")
      #      st.error("😕 Password incorrect")
      #      st.stop()
    #
    #check_password() 
    
    # -------------------------------------------------------
    
    st.set_page_config(page_title="VendoWise Dashboard", layout="wide")
    st.sidebar.image("Iniksa-TM.png", width=150)
    st.sidebar.title("Your Supplier Risk Intelligence Hub")
    nav = st.sidebar.radio("Go to", ["Dashboard", "PO Entry Simulation", "Configuration Panel"])
    
    config_path = "vendowise_config.json"
    default_config = {
        "use_rejected_qty": True,
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
    
    if not os.path.exists(config_path):
        with open(config_path, "w") as f:
            json.dump(default_config, f, indent=4)
    
    with open(config_path, "r") as f:
        config = json.load(f)
    
    # Sample data toggle or upload
    data_mode = st.sidebar.radio("Choose data input mode", ["Sample Data", "Upload CSV"])
    if data_mode == "Sample Data":
        df = pd.DataFrame({
            "Supplier": ["Alpha", "Bravo", "Charlie", "Delta", "Echo"],
            "ordered_qty": [100, 200, 150, 300, 180],
            "received_qty": [100, 180, 150, 250, 180],
            "rejected_qty": [0, 10, 6, 25, 1],
            "expected_delivery_date": pd.to_datetime(["2025-07-10", "2025-07-12", "2025-07-14", "2025-07-16", "2025-07-18"]),
            "actual_delivery_date": pd.to_datetime(["2025-07-12", "2025-07-20", "2025-07-14", "2025-07-25", "2025-07-18"]),
            "payment_terms_days": [45, 90, 30, 60, 30],
            "stock_buffer_days": [10, 5, 12, 3, 15],
            "location_risk": [2, 6, 3, 7, 1]
        })
    else:
        uploaded_file = st.sidebar.file_uploader("Upload Vendor Data CSV", type="csv")
        if uploaded_file:
            df = pd.read_csv(uploaded_file, parse_dates=["expected_delivery_date", "actual_delivery_date"])
        else:
            st.warning("Please upload a CSV file to proceed.")
            st.stop()
    
    # Risk calculation
    def risk_flags(row):
        delay = (row["actual_delivery_date"] - row["expected_delivery_date"]).days
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
        return ", ".join(flags)
    
    df["Risk Reasons"] = df.apply(risk_flags, axis=1)
    
    if nav == "Dashboard":
        st.title("📊 Supplier Risk Dashboard")
        st.dataframe(df)
    
        # Bar Chart
        all_reasons = df["Risk Reasons"].str.split(", ").explode().dropna()
        if not all_reasons.empty:
            reason_counts = all_reasons.value_counts()
            fig, ax = plt.subplots(figsize=(8, 4))
            sns.barplot(x=reason_counts.index, y=reason_counts.values, ax=ax)
            ax.set_title("Risk Reasons Frequency")
            ax.set_ylabel("Count")
            ax.set_xlabel("Reason")
            plt.xticks(rotation=45)
            st.pyplot(fig)
    
    elif nav == "PO Entry Simulation":
        st.title("📦 PO Entry Simulation")
        st.write("This panel will simulate PO creation and alert users if risk thresholds are exceeded.")
        st.dataframe(df[["Supplier", "ordered_qty", "received_qty", "expected_delivery_date", "actual_delivery_date", "Risk Reasons"]])
    
    elif nav == "Configuration Panel":
        st.title("⚙️ Configuration Settings")
        with st.form("config_form"):
            st.subheader("Toggle Parameters")
            config["use_rejected_qty"] = st.checkbox("Use Rejected Quantity", value=config["use_rejected_qty"])
            config["use_payment_terms"] = st.checkbox("Use Payment Terms", value=config["use_payment_terms"])
            config["use_stock_buffer"] = st.checkbox("Use Stock Buffer", value=config["use_stock_buffer"])
            config["use_location_risk"] = st.checkbox("Use Location Risk", value=config["use_location_risk"])
            config["use_partial_delivery"] = st.checkbox("Use Partial Delivery", value=config["use_partial_delivery"])
            st.subheader("Thresholds")
            config["thresholds"]["delay_days"] = st.slider("Max Acceptable Delay (days)", 0, 30, config["thresholds"]["delay_days"])
            config["thresholds"]["rejection_rate"] = st.slider("Max Rejection Rate", 0.0, 0.2, config["thresholds"]["rejection_rate"])
            config["thresholds"]["payment_terms_days"] = st.slider("Max Payment Terms (days)", 15, 120, config["thresholds"]["payment_terms_days"])
            config["thresholds"]["min_stock_buffer_days"] = st.slider("Min Stock Buffer (days)", 0, 30, config["thresholds"]["min_stock_buffer_days"])
            config["thresholds"]["max_location_risk"] = st.slider("Max Location Risk", 0, 10, config["thresholds"]["max_location_risk"])
    
            submitted = st.form_submit_button("💾 Save Settings")
            if submitted:
                with open(config_path, "w") as f:
                    json.dump(config, f, indent=4)
                st.success("Configuration saved!")
    

elif nav == "Inventory Risk":
    
    import streamlit as st
    
    # 🔒 Simple login protection
    def login():
        st.title("🔐 Login Required")
        user = st.text_input("Username")
        pwd = st.text_input("Password", type="password")
        if st.button("Login"):
            if user == "admin" and pwd == "admin":
                st.session_state.logged_in = True
            else:
                st.error("Invalid credentials")
    
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    
    if not st.session_state.logged_in:
        login()
        st.stop()
    
    
    import streamlit as st
    import pandas as pd
    import matplotlib.pyplot as plt
    from datetime import datetime, timedelta
    
    st.set_page_config(page_title="Inventory Buffer Risk Forecast", layout="wide")
    st.title("📦 Inventory Buffer Risk Forecast + Delay Predictor")
    
    @st.cache_data
    def load_data():
        return pd.read_csv("inventory_data.csv")
    
    df = load_data()
    df["Next PO Delivery Date"] = pd.to_datetime(df["Next PO Delivery Date"], errors="coerce")
    today = datetime(2025, 7, 17)
    
    def compute_risk(row):
        if pd.isna(row["Next PO Delivery Date"]):
            return "No PO ❓"
        delivery_date = row["Next PO Delivery Date"] + timedelta(days=row["Expected Delay (days)"])
        days_until_delivery = (delivery_date - today).days
        days_until_stockout = row["Current Stock (Qty)"] / row["Daily Avg Consumption"]
        buffer_threshold = row["Buffer Stock (days)"]
        if days_until_stockout < buffer_threshold and days_until_delivery > days_until_stockout:
            return "High Risk 🔴"
        else:
            return "Low Risk 🟢"
    
    df["Risk Status"] = df.apply(compute_risk, axis=1)
    
    tab1, tab2 = st.tabs(["📊 Dashboard", "📝 Simulate PO"])
    
    with tab1:
        st.subheader("Risk Forecast Overview")
        st.dataframe(df)
    
        # Risk Summary Bar Chart
        risk_counts = df["Risk Status"].value_counts()
        fig, ax = plt.subplots()
        risk_counts.plot(kind='bar', color=["red" if "High" in x else "green" if "Low" in x else "gray" for x in risk_counts.index], ax=ax)
        ax.set_ylabel("Number of Items")
        ax.set_title("Inventory Risk Classification")
        st.pyplot(fig)
    
    with tab2:
        st.subheader("Simulate New PO Entry")
    
        item_code = st.text_input("Item Code", "ITEM9999")
        stock_qty = st.number_input("Current Stock (Qty)", 0, 10000, 300)
        daily_usage = st.number_input("Daily Avg Consumption", 1, 1000, 30)
        buffer_days = st.number_input("Buffer Stock (days)", 1, 30, 5)
        po_date = st.date_input("Next PO Delivery Date", value=today + timedelta(days=5))
        po_qty = st.number_input("PO Delivery Qty", 0, 10000, 200)
        delay = st.number_input("Expected Delay (days)", 0, 15, 2)
    
        if st.button("Check Risk"):
            days_until_delivery = (po_date + timedelta(days=delay) - today).days
            days_until_stockout = stock_qty / daily_usage
            risk = "High Risk 🔴" if days_until_stockout < buffer_days and days_until_delivery > days_until_stockout else "Low Risk 🟢"
            st.success(f"Predicted Risk for {item_code}: **{risk}**")

elif nav == "Configuration":
    st.markdown("### ⚙️ Current Config")
    st.json(config)
    uploaded_config = st.file_uploader("Upload New Config File", type=["json"])
    if uploaded_config:
        with open("vendowise_config.json", "wb") as f:
            f.write(uploaded_config.read())
        st.success("✅ Configuration updated. Please reload app.")
