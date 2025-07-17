import numpy as np
from sklearn.ensemble import RandomForestClassifier
import joblib

# ----------------------------
# 1. Prepare training data
# ----------------------------
# Features: [Avg_Delay_Days, Rejection_Rate]
X = np.array([
    [2, 0.02],
    [7, 0.07],
    [4, 0.04],
    [10, 0.10],
    [1, 0.01]
])
y = np.array([0, 1, 0, 1, 0])

# ----------------------------
# 2. Train the model
# ----------------------------
model = RandomForestClassifier(n_estimators=10, random_state=42)
model.fit(X, y)

# ----------------------------
# 3. Save the model
# ----------------------------
joblib.dump(model, "mock_supplier_risk_model.pkl")
print("✅ Model saved as 'mock_supplier_risk_model.pkl'")
