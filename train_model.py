import pandas as pd
import numpy as np
import joblib

from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

from features import build_features
from database import SessionLocal
from models import LabResult


# -------------------------
# LOAD DATA FROM DB
# -------------------------
db = SessionLocal()
data = db.query(LabResult).all()
db.close()

df = pd.DataFrame([{
    "sample_id": r.sample_id,
    "timestamp": float(r.timestamp),
    "sensor_index": int(r.instrument.split("_")[1]),
    "value": r.value
} for r in data])

# -------------------------
# FEATURE ENGINEERING
# -------------------------
df = build_features(df)

# -------------------------
# CREATE RUL LABEL
# -------------------------
max_cycle = df.groupby("sample_id")["timestamp"].transform("max")
df["rul"] = max_cycle - df["timestamp"]

# -------------------------
# TRAIN DATASET
# -------------------------
features = [
    "value",
    "rolling_mean",
    "rolling_std",
    "diff",
    "sensor_index"
]

X = df[features]
y = df["rul"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# -------------------------
# MODEL
# -------------------------
model = RandomForestRegressor(
    n_estimators=150,
    max_depth=12,
    random_state=42
)

model.fit(X_train, y_train)

# -------------------------
# SAVE MODEL
# -------------------------
joblib.dump(model, "model.pkl")

print("Model trained and saved as model.pkl")