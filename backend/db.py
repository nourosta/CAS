from sqlalchemy import create_engine, Table, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker
from pathlib import Path
import sqlite3


DB_PATH = "sqlite:///./data/data.db"
engine = create_engine(DB_PATH, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(engine)

Base = declarative_base()

# Create a model for your data
class PowerBreakdown(Base):
    __tablename__ = "power_breakdown"

    id = Column(Integer, primary_key=True, index=True)
    zone = Column(String, index=True)
    data = Column(String)  # Store JSON data as text, or you can create specific columns for individual fields

# New model for storing carbon intensity
class CarbonIntensity(Base):
    __tablename__ = "carbon_intensity"
    id = Column(Integer, primary_key=True, index=True)
    zone = Column(String, index=True)
    data = Column(String)

#create database tables
def init_db():
    Base.metadata.create_all(bind=engine, checkfirst = True)

# Direct SQLite interaction example
def direct_sqlite_init():
    conn = sqlite3.connect("data/data.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS power_breakdown (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            zone TEXT NOT NULL,
                            data TEXT NOT NULL)''')
    conn.commit()
    conn.close()

# Function to add data to the database
def store_power_breakdown(zone: str, data: dict):
    db = SessionLocal()
    try:
        # Store the data
        power_data = PowerBreakdown(zone=zone, data=str(data))  # Convert dict to string if necessary
        db.add(power_data)
        db.commit()
        db.refresh(power_data)
        return power_data
    finally:
        db.close()

def store_carbon_intensity(zone: str, data: dict):
    db = SessionLocal()
    try:
        intensity_data = CarbonIntensity(zone=zone, data=str(data))
        db.add(intensity_data)
        db.commit()
        db.refresh(intensity_data)
        return intensity_data
    finally:
        db.close()