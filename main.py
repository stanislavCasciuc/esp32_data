import datetime
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import DateTime, create_engine, Column, Integer, Float, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Configurare PostgreSQL"postgresql://postgres:postgres@localhost:5432/esp32_data"
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/esp32_data")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Definirea modelului bazei de date
class SensorData(Base):
    __tablename__ = "sensor_data"
    id = Column(Integer, primary_key=True, index=True)
    temperature = Column(Float, nullable=False)
    humidity = Column(Float, nullable=False)
    left_flower = Column(Float, nullable=False)
    right_flower = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

# Creare tabele în baza de date
inspector = inspect(engine)
if not inspector.has_table("sensor_data"):
    Base.metadata.create_all(bind=engine)

# Definirea API-ului
app = FastAPI()

# Model pentru datele primite
class SensorDataRequest(BaseModel):
    temperature: float
    humidity: float
    left_flower: float
    right_flower: float

@app.post("/data")
def receive_data(data: SensorDataRequest):
    db = SessionLocal()
    sensor_entry = SensorData(temperature=data.temperature, humidity=data.humidity, left_flower=data.left_flower, right_flower=data.right_flower)
    db.add(sensor_entry)
    db.commit()
    db.refresh(sensor_entry)
    db.close()
    return {"message": "Data saved successfully", "id": sensor_entry.id}

@app.get("/data/last")
def get_last_data():
    db = SessionLocal()
    last_entry = db.query(SensorData).order_by(SensorData.id.desc()).first()
    db.close()
    if last_entry is None:
        raise HTTPException(status_code=404, detail="No data found")
    return {"temperature": last_entry.temperature, "humidity": last_entry.humidity, "created_at": last_entry.created_at, "left_flower": last_entry.left_flower, "right_flower": last_entry.right_flower}


@app.get("/data/all")
def get_all_data():
    db = SessionLocal()
    all_entries = db.query(SensorData).all()
    db.close()
    return all_entries

if __name__ == "__main__":
  import uvicorn
  uvicorn.run(app, host="0.0.0.0", port=8000)
