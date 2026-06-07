from fastapi import FastAPI, UploadFile, File
import pandas as pd
from database import engine, Base, SessionLocal
from models import LabResult

Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    # read uploaded CSV
    df = pd.read_csv(file.file)

    # basic normalisation
    df.columns = [c.lower() for c in df.columns]

    db = SessionLocal()

    for _, row in df.iterrows():
        db.add(LabResult(
            sample_id=str(row["sample_id"]),
            timestamp=str(row["timestamp"]),
            instrument=str(row["instrument"]),
            value=float(row["value"]),
            unit=str(row["unit"])
        ))

    db.commit()
    db.close()

    return {"status": "file processed", "rows": len(df)}