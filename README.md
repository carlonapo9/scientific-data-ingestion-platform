## 🚀 Live Demo

🔗 **Web App:** https://carlonapo9-scientific-data-ingestion-platform-app-ui-tibicg.streamlit.app/

Hosted on Streamlit Cloud — no setup required.

---

## 📊 Scientific Data Ingestion Platform

# Scientific Data Ingestion Platform

Python platform for ingesting, processing, and analysing scientific sensor and lab instrument data.

## Features
- CSV / TXT ingestion from lab-style datasets (e.g. NASA sensor data)
- FastAPI backend for data upload and processing
- SQL database storage using SQLAlchemy
- Streamlit UI for exploration and visualisation
- Sensor-level structuring and pivot views
- Basic predictive metrics (health score, risk ranking)
- Anomaly detection using statistical methods (z-score)

## Tech Stack
- Python
- FastAPI
- Streamlit
- Pandas
- SQLAlchemy
- Scikit-learn

## Use Case
Designed as a simplified simulation of scientific data integration systems used in lab environments, where instrument outputs must be cleaned, structured, and made queryable.

## Run Locally
```bash
pip install -r requirements.txt
uvicorn main:app --reload
streamlit run app_ui.py
