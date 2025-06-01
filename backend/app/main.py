import subprocess
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests, json
from electricitymaps import fetch_power_breakdown
from carbon_intensity import fetch_carbon_intensity
from db import init_db, store_power_breakdown, store_carbon_intensity
from gpu_scraper import scrape_and_store_gpu_data
from datetime import datetime
import os
from dbgpu import GPUDatabase
#from apscheduler.schedulers.background import BackgroundScheduler

app = FastAPI()


# Initialize the database
@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/")
async def read_root():
    return {"message": "Welcome to the Backend API"}

@app.post("/get-config/")
async def get_config():
    try:
        # get config script
        result = subprocess.run(
            ["lshw" ,"-json"],
            capture_output=True,
            text=True,
            check=True
        )
        return {"success": True, "output": result.stdout}
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Script execution failed: {e.stderr}")
    

@app.get("/boavizta_cpu_name/")
async def get_boavizta_cpu_name():
    try:
        response = requests.get("http://boaviztapi:5000/v1/utils/cpu_name", headers={"accept": "application/json"})
        response.raise_for_status()  # Handle HTTP errors
        return response.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Failed to connect to Boavizta API: {str(e)}")
    


@app.post("/run-energizta/")
async def run_energizta():
    try:
        # Execute the Energizta script
        result = subprocess.run(
            ["sudo", "bash", "./energizta.sh", "--interval", "1", "--duration", "60", "--once"],
            capture_output=True,
            text=True,
            check=True
        )
        return {"success": True, "output": result.stdout}
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Script execution failed: {e.stderr}")




# Define a Pydantic model for input validation
class RAMSpec(BaseModel):
    capacity: int
    manufacturer: str
    process: int

@app.post("/RAM-Calc")
async def ram_calc(ram_spec: RAMSpec):
    try:
        # Use the inputs provided by the user
        payload = ram_spec.dict()  # Assuming direct usage, adjust as necessary for API
        #print(payload)
        # Modify this request based on how you need to use these inputs in Boavizta API
        response = requests.post("http://boaviztapi:5000/v1/component/ram", headers={"accept": "application/json"}, json=payload)
        #print(response.json())
        response.raise_for_status()  # Handle HTTP errors
        return response.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Failed to connect to Boavizta API: {str(e)}")
    
# Define a Pydantic model for input validation
class CPUSpec(BaseModel):
    name : str

@app.post("/CPU-Calc")
async def cpu_calc(cpu_spec: CPUSpec):
    try:
        # Use the inputs provided by the user
        payload = cpu_spec.dict()  # Assuming direct usage, adjust as necessary for API
        print(payload)
        # Modify this request based on how you need to use these inputs in Boavizta API
        response = requests.post("http://boaviztapi:5000/v1/component/cpu", headers={"accept": "application/json"}, json=payload)
        print(response.json())
        response.raise_for_status()  # Handle HTTP errors
        return response.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Failed to connect to Boavizta API: {str(e)}")
    
# Define a Pydantic model for input validation
class SSDSpec(BaseModel):
    capacity : int
    manufacturer : str

@app.post("/SSD-Calc")
async def ssd_calc(ssd_spec: SSDSpec):
    try:
        # Use the inputs provided by the user
        payload = ssd_spec.dict()  # Assuming direct usage, adjust as necessary for API
        print(payload)
        # Modify this request based on how you need to use these inputs in Boavizta API
        response = requests.post("http://boaviztapi:5000/v1/component/ssd", headers={"accept": "application/json"}, json=payload)
        print(response.json())
        response.raise_for_status()  # Handle HTTP errors
        return response.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Failed to connect to Boavizta API: {str(e)}")
    
# Define a Pydantic model for input validation
class HDDSpec(BaseModel):
    units : int
    type : str
    capacity : int

@app.post("/HDD-Calc")
async def hdd_calc(hdd_spec: HDDSpec):
    try:
        # Use the inputs provided by the user
        payload = hdd_spec.dict()  # Assuming direct usage, adjust as necessary for API
        print(payload)
        # Modify this request based on how you need to use these inputs in Boavizta API
        response = requests.post("http://boaviztapi:5000/v1/component/hdd", headers={"accept": "application/json"}, json=payload)
        print(response.json())
        response.raise_for_status()  # Handle HTTP errors
        return response.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Failed to connect to Boavizta API: {str(e)}")
    

# Define a Pydantic model for input validation
class CaseSpec(BaseModel):
    case_type : str

@app.post("/Case-Calc")
async def case_calc(case_spec: CaseSpec):
    try:
        # Use the inputs provided by the user
        payload = case_spec.dict()  # Assuming direct usage, adjust as necessary for API
        print(payload)
        # Modify this request based on how you need to use these inputs in Boavizta API
        response = requests.post("http://boaviztapi:5000/v1/component/case", headers={"accept": "application/json"}, json=payload)
        print(response.json())
        response.raise_for_status()  # Handle HTTP errors
        return response.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Failed to connect to Boavizta API: {str(e)}")

@app.get("/power-breakdown")
async def get_power_breakdown(zone: str = 'FR'):
    try:
        #fetch data from elecricitymaps
        data = fetch_power_breakdown(zone)

        #Store data in database
        store_power_breakdown(zone,data)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# New endpoint for carbon intensity
@app.get("/carbon-intensity")
async def get_carbon_intensity(zone: str = 'FR'):
    try:
        data = fetch_carbon_intensity(zone)
        store_carbon_intensity(zone, data)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    


@app.get("/system-info")
def get_system_info():
    try:
        with open("/output/system_info.txt", "r") as f:  # Adjust path as needed
            return {"system_info": f.read()}
    except FileNotFoundError:
        return {"error": "System information file not found."}
    except Exception as e:
        return {"error": str(e)}

    

database = GPUDatabase.default()
@app.get("/gpu-specs")
def get_gpu_specs(model: str):
    
    spec = database.search(model.strip())
    if not spec:
        raise HTTPException(status_code=404, detail="GPU not found")
    
    return {
        "die_size": spec.get("die_size", 0.0),
        "ram_size": spec.get("ram_size", 1),
    }
