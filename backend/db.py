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

# Define GPU Model with detailed specification fields
class GPUInfo(Base):
    __tablename__ = "gpu_info"
    id = Column(Integer, primary_key=True, index=True)
    manufacturer = Column(String, nullable=False)
    name = Column(String, nullable=False)
    gpu_name = Column(String, nullable=False)
    generation = Column(String, nullable=True)
    base_clock_mhz = Column(Float, nullable=True)
    boost_clock_mhz = Column(Float, nullable=True)
    architecture = Column(String, nullable=True)
    foundry = Column(String, nullable=True)
    process_size_nm = Column(Integer, nullable=True)
    transistor_count_m = Column(Float, nullable=True)
    transistor_density_k_mm2 = Column(Float, nullable=True)
    die_size_mm2 = Column(Float, nullable=True)
    chip_package = Column(String, nullable=True)
    release_date = Column(Date, nullable=True)
    bus_interface = Column(String, nullable=True)
    memory_clock_mhz = Column(Float, nullable=True)
    memory_size_gb = Column(Float, nullable=True)
    memory_bus_bits = Column(Integer, nullable=True)
    memory_bandwidth_gb_s = Column(Float, nullable=True)
    memory_type = Column(String, nullable=True)
    shading_units = Column(Integer, nullable=True)
    texture_mapping_units = Column(Integer, nullable=True)
    render_output_processors = Column(Integer, nullable=True)
    streaming_multiprocessors = Column(Integer, nullable=True)
    tensor_cores = Column(Integer, nullable=True)
    ray_tracing_cores = Column(Integer, nullable=True)
    l1_cache_kb = Column(Float, nullable=True)
    l2_cache_mb = Column(Float, nullable=True)
    thermal_design_power_w = Column(Integer, nullable=True)
    board_length_mm = Column(Float, nullable=True)
    board_width_mm = Column(Float, nullable=True)
    board_slot_width = Column(String, nullable=True)
    suggested_psu_w = Column(Integer, nullable=True)
    power_connectors = Column(String, nullable=True)
    display_connectors = Column(String, nullable=True)
    directx_major_version = Column(Integer, nullable=True)
    directx_minor_version = Column(Integer, nullable=True)
    opengl_major_version = Column(Integer, nullable=True)
    opengl_minor_version = Column(Integer, nullable=True)
    vulkan_major_version = Column(Integer, nullable=True)
    vulkan_minor_version = Column(Integer, nullable=True)
    opencl_major_version = Column(Integer, nullable=True)
    opencl_minor_version = Column(Integer, nullable=True)
    cuda_major_version = Column(Integer, nullable=True)
    cuda_minor_version = Column(Integer, nullable=True)
    shader_model_major_version = Column(Integer, nullable=True)
    shader_model_minor_version = Column(Integer, nullable=True)
    pixel_rate_gpixel_s = Column(Float, nullable=True)
    texture_rate_gtexel_s = Column(Float, nullable=True)
    half_float_performance_gflop_s = Column(Float, nullable=True)
    single_float_performance_gflop_s = Column(Float, nullable=True)
    double_float_performance_gflop_s = Column(Float, nullable=True)
    tpu_id = Column(String, nullable=True)
    tpu_url = Column(String, nullable=True)


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

def store_gpu_data(**kwargs):
    db = SessionLocal()
    try:
        gpu_data = GPUInfo(**kwargs)
        db.add(gpu_data)
        db.commit()
        db.refresh(gpu_data)
        return gpu_data
    finally:
        db.close()