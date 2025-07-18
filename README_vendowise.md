# VendoWise - Supplier Risk Evaluator

**VendoWise** is a smart supplier performance and risk evaluation tool designed for procurement teams.

## 🚀 Features

- Upload vendor PO and delivery data
- Toggle and configure risk factors:
  - Delivery delay
  - Rejection rate
  - Payment terms
  - Stock buffer
  - Location risk
- Smart alerts for each vendor
- Interactive bar chart showing risk reasons
- Password protection for app access

## 🔧 Configuration

Configuration can be modified via the sidebar or by editing `vendowise_config.json`.

## 🔑 Login

Default password: `vendowise123`

## 📁 Required Files

- `vendowise_dynamic_risk_chart_protected.py`
- `requirements.txt`
- `vendor_data.csv` (sample input)
- `vendowise_config.json`

## 📊 Sample Output

- Visual table with vendor risk levels
- Bar chart showing frequency of each risk reason

## 🧪 How to Deploy on Streamlit

1. Push code to GitHub
2. Go to [Streamlit Cloud](https://share.streamlit.io)
3. Connect to your repo and set:
   - Main file: `vendowise_dynamic_risk_chart_protected.py`
   - Branch: `main`
4. Click Deploy

