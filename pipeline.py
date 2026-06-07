from database import SessionLocal
from models import LabResult

def save_to_db(df):
    db = SessionLocal()

    for _, row in df.iterrows():

        engine_id = str(row[0])
        cycle = str(row[1])

        for i, value in enumerate(row[2:]):

            db.add(LabResult(
                sample_id=engine_id,
                timestamp=cycle,
                instrument=f"sensor_{i}",
                value=float(value),
                unit="raw"
            ))

    db.commit()
    db.close()