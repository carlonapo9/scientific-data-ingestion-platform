from sqlalchemy import Column, Integer, String, Float
from database import Base

class LabResult(Base):
    __tablename__ = "lab_results"

    id = Column(Integer, primary_key=True, index=True)
    sample_id = Column(String)
    timestamp = Column(String)
    instrument = Column(String)
    value = Column(Float)
    unit = Column(String)