# 🧠 VendoWise – Supplier Risk Intelligence Dashboard

**VendoWise** is a smart, lightweight AI-enabled web app built using [Streamlit](https://streamlit.io/) to help procurement and supply chain teams make faster, data-backed decisions about supplier risks.

> ✅ Predict delays, detect quality issues, and simulate risks — before issuing a Purchase Order.

---

## 🔍 Features

- 📊 **Dashboard View**: Visualize average delivery delays and rejection rates by supplier.
- 🚨 **Risk Alerts**: Automatic scoring based on delay & quality thresholds.
- 🧾 **PO Entry Simulation**: Check supplier risk score before creating a PO.
- 🔧 **Configurable Settings**: Adjust thresholds and upload your own data.
- 🧠 **AI-Ready Architecture**: Built with future ML integration in mind.

---

## 🖥 Demo Preview

🔒 Password Protected Demo: `vendowise123`

**Live App**: [https://your-username-vendowise-ui-app.streamlit.app](https://your-username-vendowise-ui-app.streamlit.app)

---

## 📁 Folder Structure

```
vendowise-ui-app/
│
├── vendowise_corrected_final.py      # Main Streamlit app
├── requirements.txt                  # Python dependencies
├── .streamlit/
│   └── config.toml                   # Custom theme settings
├── README.md                         # This file
└── sample_data.csv                   # Optional sample supplier data
```

---

## 🛠 How to Run Locally

```bash
git clone https://github.com/YOUR_USERNAME/vendowise-ui-app.git
cd vendowise-ui-app
pip install -r requirements.txt
streamlit run vendowise_corrected_final.py
```

---

## 📤 Upload Format

Your uploaded `.csv` should contain:

| Supplier | Avg_Delay_Days | Rejection_Rate | Historical_Orders |
|----------|----------------|----------------|--------------------|
| Alpha    | 3              | 0.02           | 50                 |

---

## 💡 Future Enhancements

- Integration with ERP systems like Oracle, SAP, Odoo
- Predictive AI/ML models for real-time supplier risk forecasting
- Multi-user login & approval flows
- Deal value, delivery location & cost risk layers

---

## 👤 Built By

**Snehal Jibkate**  
ERP & Data Strategy Consultant with 28+ years of experience in project management, ERP implementation, and analytics.

🌐 [LinkedIn](https://www.linkedin.com/in/snehaljibkate)  
📧 vendowise@eniksa.com  

---

## 📄 License

MIT License. Free to use, customize, and build upon.

---

## ⭐ Star this repo if you like the idea — let’s make supply chains smarter!
