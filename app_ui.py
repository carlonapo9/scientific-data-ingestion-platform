import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler

from database import SessionLocal
from models import LabResult
from pipeline import save_to_db

st.title("Lab Data Ingestion Platform (NASA Predictive Edition)")

# =========================================================
# RESET DATABASE
# =========================================================
if st.button("RESET DATABASE"):
    db = SessionLocal()
    db.query(LabResult).delete()
    db.commit()
    db.close()

    # reset upload lock so new file can be loaded again
    st.session_state["uploaded_once"] = False

    st.success("Database cleared")

# =========================================================
# SESSION STATE
# =========================================================
if "uploaded_once" not in st.session_state:
    st.session_state["uploaded_once"] = False

# =========================================================
# UPLOAD
# =========================================================
st.subheader("Upload Data")

uploaded_file = st.file_uploader("Upload dataset", type=["csv", "txt"])

if uploaded_file is not None and not st.session_state["uploaded_once"]:

    df_raw = pd.read_csv(uploaded_file, sep=r"\s+", header=None)

    save_to_db(df_raw)

    st.session_state["uploaded_once"] = True

    st.success(f"Uploaded {len(df_raw)} rows")

# =========================================================
# LOAD FROM DB
# =========================================================
db = SessionLocal()
data = db.query(LabResult).all()
db.close()

rows = [
    {
        "sample_id": r.sample_id,
        "timestamp": r.timestamp,
        "instrument": r.instrument,
        "value": r.value,
        "unit": r.unit,
    }
    for r in data
]

df = pd.DataFrame(rows)

if df.empty:
    st.stop()

# =========================================================
# CLEAN + TYPE FIX
# =========================================================
df["sample_id"] = pd.to_numeric(df["sample_id"], errors="coerce")
df["timestamp"] = pd.to_numeric(df["timestamp"], errors="coerce")
df["value"] = pd.to_numeric(df["value"], errors="coerce")

df = df.dropna()

# FIX SENSOR INDEX (robust numeric extraction)
df["sensor_index"] = df["instrument"].str.extract(r"(\d+)").astype(int)

# =========================================================
# HEALTH SCORE
# =========================================================
baseline = df.groupby("sensor_index")["value"].mean()
df["baseline"] = df["sensor_index"].map(baseline)

df["deviation"] = (df["value"] - df["baseline"]).abs()

engine_health = df.groupby("sample_id").agg(
    avg_dev=("deviation", "mean"),
    max_dev=("deviation", "max")
).reset_index()

scaler = MinMaxScaler()
engine_health[["avg_dev", "max_dev"]] = scaler.fit_transform(
    engine_health[["avg_dev", "max_dev"]]
)

engine_health["health_score"] = 100 * (
    1 - (0.7 * engine_health["avg_dev"] + 0.3 * engine_health["max_dev"])
)

engine_health["health_score"] = engine_health["health_score"].clip(0, 100)

st.subheader("Engine Health Score")

st.dataframe(engine_health.sort_values("health_score", ascending=False))

worst_health = engine_health.loc[engine_health["health_score"].idxmin()]

st.warning(
    f"Lowest health engine: {worst_health['sample_id']} "
    f"(Score: {worst_health['health_score']:.2f})"
)

# =========================================================
# RISK SCORE
# =========================================================
engine_life = df.groupby("sample_id")["timestamp"].max().reset_index()
engine_life.columns = ["sample_id", "max_cycle"]

df = df.merge(engine_life, on="sample_id", how="left")

df["rul"] = df["max_cycle"] - df["timestamp"]

engine_risk = df.groupby("sample_id").agg(
    mean_rul=("rul", "mean")
).reset_index()

engine_risk["mean_rul"] = MinMaxScaler().fit_transform(
    engine_risk[["mean_rul"]]
)

engine_risk["risk_score"] = 100 * (1 - engine_risk["mean_rul"])

st.subheader("Engine Failure Risk Ranking")

st.dataframe(engine_risk.sort_values("risk_score", ascending=False))

worst_risk = engine_risk.loc[engine_risk["risk_score"].idxmax()]

st.error(
    f"Highest risk engine: {worst_risk['sample_id']} "
    f"(Risk Score: {worst_risk['risk_score']:.2f})"
)

# =========================================================
# SENSOR MATRIX VIEW
# =========================================================
st.subheader("Sensor Matrix View")

wide_df = df.pivot_table(
    index=["sample_id", "timestamp"],
    columns="sensor_index",
    values="value"
).reset_index()

# FIX COLUMN ORDERING (numeric, not lexicographic)
sensor_cols = sorted([c for c in wide_df.columns if isinstance(c, int)])

wide_df = wide_df[["sample_id", "timestamp"] + sensor_cols]

st.dataframe(wide_df)

# =========================================================
# SENSOR TREND + ANOMALY
# =========================================================
st.subheader("Sensor Trend + Anomalies")

engine_ids = sorted(df["sample_id"].unique())
selected_engine = st.selectbox("Select Engine", engine_ids)

sensor_ids = sorted(df["sensor_index"].unique().astype(int))
selected_sensor = st.selectbox("Select Sensor", sensor_ids)

filtered = df[
    (df["sample_id"] == selected_engine) &
    (df["sensor_index"] == selected_sensor)
].sort_values("timestamp")

mean = filtered["value"].mean()
std = filtered["value"].std() if filtered["value"].std() != 0 else 1

filtered["z"] = (filtered["value"] - mean) / std
anomalies = filtered[filtered["z"].abs() > 3]

fig, ax = plt.subplots()

ax.plot(filtered["timestamp"], filtered["value"], label="Signal")

ax.scatter(
    anomalies["timestamp"],
    anomalies["value"],
    color="red",
    label="Anomaly"
)

ax.set_xlabel("Cycle")
ax.set_ylabel("Value")
ax.set_title(f"Engine {selected_engine} - Sensor {selected_sensor}")
ax.legend()

st.pyplot(fig)