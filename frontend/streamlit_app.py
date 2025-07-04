import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from backend.electricitymaps import fetch_power_breakdown
from backend.carbon_intensity import fetch_carbon_intensity
import subprocess
import math
from dbgpu import GPUDatabase

st.title("Carbon as a Service" )

FASTAPI_BASE_URL = "http://backend:8000" 

response = requests.get("http://backend:8000/")

#if response.status_code == 200:
#    st.write(response.json()["message"])
#else:
#    st.error("Failed to connect to the backend")



def Calculate_GPU_impact(die_size, ram_size):
    # Convert die size from cm² to mm² for calculation
    die_mm = die_size / 100  # Convert cm² to m² and then cm² to mm²
    ram_gb = ram_size  # RAM size in GB
    
    # Impact factors for the GPU die
    die_gwp = 1.97  # GWP for die in kgCO2 eq
    die_adp = 5.80E-07  # ADP for die in kgSbeq
    die_pe = 26.50  # PE for die in MJ
    
    # Impact factors for RAM
    ram_gwp = 2.20  # GWP for RAM per unit density in kgCO2 eq
    ram_adp = 6.30E-05  # ADP for RAM per unit density in kgSbeq
    ram_pe = 27.30  # PE for RAM per unit density in MJ
    
    # Base impacts for RAM
    ram_base_gwp = 5.22  # Base GWP for RAM in kgCO2 eq
    ram_base_adp = 1.69E-03  # Base ADP for RAM in kgSbeq
    ram_base_pe = 74.00  # Base PE for RAM in MJ
    
    
    try:
        # Preparing payload for RAM impact calculation
        payload = {
            "capacity": ram_size,
            "manufacturer": "Samsung",
            "process": 30
        }
        # Call RAM impact API
        response = requests.post("http://backend:8000/RAM-Calc", json=payload)
        response.raise_for_status()  # Raise error for bad responses
        ram_data = response.json()

        # Retrieve RAM impacts
        impacts = ram_data.get("impacts", {})
        ram_gwp = ram_base_gwp = ram_base_adp = ram_base_pe = 0
        
        for key, impact_info in impacts.items():
            if key == "gwp":
                ram_gwp = impact_info['embedded']['value']
            elif key == "adp":
                ram_base_adp = impact_info['embedded']['value']
            elif key == "pe":
                ram_base_pe = impact_info['embedded']['value']

    except requests.RequestException as e:
        st.error(f"Failed to retrieve RAM data: {str(e)}")
        return None, None, None  # Return None values on API failure.

    # Impact factors for GPU die
    die_gwp = 1.97  # GWP for die in kgCO2 eq
    die_adp = 5.80E-07  # ADP for die in kgSbeq
    die_pe = 26.50  # PE for die in MJ
    
    # RAM density (hypothetical value)
    ram_density = 1.25  # RAM density in GB/cm² (or appropriate unit)

    # Base impact for the GPU itself
    gpu_base = 23.71  # Base impact in kgCO2 eq

    # Calculating impacts for the GPU die
    die_calc_gwp = die_mm * die_gwp
    die_calc_adp = die_mm * die_adp
    die_calc_pe = die_mm * die_pe

    # Calculating impacts for the RAM based on the values from the API
   # ram_calc_gwp = (ram_gb / ram_density) * ram_gwp + ram_base_gwp
   # ram_calc_adp = (ram_gb / ram_density) * ram_base_adp + ram_base_adp
    ram_calc_pe = (ram_gb / ram_density) * ram_base_pe + ram_base_pe

    # Total GPU impacts
    gpu_calc_gwp = die_calc_gwp + ram_gwp + gpu_base
    gpu_calc_adp = die_calc_adp + ram_adp + gpu_base
    gpu_calc_pe = die_calc_pe + ram_pe + gpu_base
    
    return gpu_calc_gwp, gpu_calc_adp, gpu_calc_pe  # Return the values



def fetch_system_info():
    try:
        response = requests.get("http://backend:8000/system-info")
        response.raise_for_status()
        data = response.json()
        return data.get("system_info", "No data found.")
    except requests.exceptions.RequestException as e:
        return f"Error fetching data: {e}"

def parse_system_info(system_info_text):
    parsed_info = {
        "CPU": "Unknown",
        "RAM": "Unknown",
        "Disk": [],
        "GPUs": []
    }

    lines = system_info_text.splitlines()
    for line in lines:
        line = line.strip()
        if line.startswith("CPU Name:"):
            parsed_info["CPU"] = line.split(": ")[1].strip()
        elif line.startswith("Total RAM:"):
            parsed_info["RAM"] = line.split(": ")[1].strip()
        elif line.startswith("Disk Info:"):
            parsed_info["Disk"].append(line.split(": ")[1].strip())
        elif line.startswith("GPU Info:"):
            parsed_info["GPUs"].append(line.split(": ")[1].strip())

    return parsed_info


def parse_disk_info(disk_info_text):
    disks = []  # List to store disk information
    
    lines = disk_info_text
    for line in lines:
        parts = line.split()
        # Ensure the format fits, and check for SSD
        if "SSD" in line and len(parts) >= 6:
            disk_type = parts[1]
            manufacturer = parts[3]
            size_str = parts[-1]

            # Convert size to GB
            if "T" in size_str:
                size_in_gb = float(size_str.replace("T", "")) * 1024  # Convert TB to GB
            elif "G" in size_str:
                size_in_gb = float(size_str.replace("G", "").replace(',','.'))  # Already in GB
            else:
                size_in_gb = "N/A"  # Unknown size format
            
            disk_info = {
                "type": disk_type,
                "size_GB": size_in_gb,
                "manufacturer": manufacturer if manufacturer not in ["N/A", "Unknown"] else "N/A"
            }
            disks.append(disk_info)

    return disks


def parse_gpu_info(gpu_info_text):
    gpus = []  # List to store GPU information

    lines = gpu_info_text
    for line in lines:
        # Check if the line contains GPU information
        if "GPU:" in line:
            parts = line.split(": ")
            if len(parts) >= 2:
                gpu_model = parts[1].strip()
                gpu_info = {
                    "model": gpu_model
                }
                gpus.append(gpu_info)

    return gpus




# Fetch the system information
system_info_text = fetch_system_info()
parsed_info = parse_system_info(system_info_text)
gpus = parse_gpu_info(parsed_info["GPUs"])

detected_cpu = parsed_info["CPU"]
detected_ram = parsed_info["RAM"]
detected_GPU = parsed_info["GPUs"]
st.title("System Information")

# Autofill fields based on the parsed CPU and RAM information
st.text(f"CPU Name: {detected_cpu}")
st.text(f"Total RAM: {detected_ram}")
#st.text(f"GPUs: {detected_GPU}")

# Parse the disk info
detected_disks = parse_disk_info(parsed_info["Disk"])

# Display disk information for each disk
for idx, disk in enumerate(detected_disks):
    st.text(f"Disk {idx + 1}:")
    st.text(f"    Type: {disk['type']}")
    st.text(f"    Size (GB): {disk['size_GB']}")
    st.text(f"    Manufacturer: {disk['manufacturer']}")
    st.text("")  # back to line

# Display GPU information for each GPU
for idx, gpu in enumerate(detected_GPU):
    st.text(f"GPU {idx + 1}:")
    st.text(f"    Model: {gpu}")
    st.text("")  # Back to line



st.title("Boavizta CPU Calculation")

st.subheader("CPU Scope3 Calculations", divider = True)



# Create input fields for RAM specifications
#cpu_name = st.text_input("Enter CPU Name:", value="intel xeon gold 6134")
cpu_name = st.text_input("Enter CPU Name:", value= parsed_info["CPU"] if parsed_info["CPU"] != "Unknown" else "intel xeon gold 6134")
left, middle, right = st.columns(3)

if right.button("Fetch CPU Data"):
    # HTTP POST request with inputs to FastAPI endpoint
    try:
        payload = {
            "name" : cpu_name
        }
        response = requests.post("http://backend:8000/CPU-Calc", json=payload)
        response.raise_for_status()  # Raise error for bad responses
        cpu_data = response.json()

        # Display the first 6 impact entries
        st.subheader("Impact Information:")

        impacts = cpu_data.get("impacts", {})
        impact_keys = list(impacts.keys())[:6]  # Get the first 6 keys

        for key in impact_keys:
            impact_info = impacts[key]
            st.text(f"{key.upper()}")
            st.text(f"Description: {impact_info['description']}")
            st.text(f"Unit: {impact_info['unit']}")
            st.text(f"Embedded Value: {impact_info['embedded']['value']} {impact_info['unit']}")
            #st.text(f"Using value: {impact_info['use']['value']} {impact_info['unit']}")

            # Display warning messages if any
            #if 'warnings' in impact_info['embedded']:
            #    for warning in impact_info['embedded']['warnings']:
             #       st.warning(warning)

            st.text("")  # Add a line break

    except requests.RequestException as e:
        st.error(f"Failed to retrieve CPU data: {str(e)}")

st.title("Boavizta RAM Calculation")
st.subheader("RAM Scope3 Calculations", divider = True)

# Create input fields for RAM specifications
ram_capacity = st.number_input("Enter RAM Capacity (GB):", min_value=1, value=int(math.ceil(float(parsed_info["RAM"].split()[0]) if parsed_info["RAM"] != "Unknown" else 32)))
ram_manufacturer = st.text_input("Enter RAM Manufacturer:", value="Samsung")
ram_process = st.number_input("Enter Process (nm):", min_value=1, max_value=100, value=30)
left, middle, right = st.columns(3)

if right.button("Fetch RAM Data"):
    # HTTP POST request with inputs to FastAPI endpoint
    try:
        payload = {
            "capacity": ram_capacity,
            "manufacturer": ram_manufacturer,
            "process": ram_process
        }
        response = requests.post("http://backend:8000/RAM-Calc", json=payload)
        response.raise_for_status()  # Raise error for bad responses
        ram_data = response.json()

        # Display the first 6 impact entries
        st.subheader("Impact Information:")

        impacts = ram_data.get("impacts", {})
        impact_keys = list(impacts.keys())[:6]  # Get the first 6 keys

        for key in impact_keys:
            impact_info = impacts[key]
            st.text(f"{key.upper()}")
            st.text(f"Description: {impact_info['description']}")
            st.text(f"Unit: {impact_info['unit']}")
            st.text(f"Embedded Value: {impact_info['embedded']['value']} {impact_info['unit']}")
           # st.text(f"Using value: {impact_info['use']['value']} {impact_info['unit']}")

            # Display warning messages if any
            #if 'warnings' in impact_info['embedded']:
            #    for warning in impact_info['embedded']['warnings']:
             #       st.warning(warning)

            st.text("")  # Add a line break

    except requests.RequestException as e:
        st.error(f"Failed to retrieve RAM data: {str(e)}")


st.title("Storage Scope3 Calculation")

st.subheader("Boavizta SSD Calculations", divider = True)


# Separate SSDs and HDDs
ssds = [disk for disk in detected_disks if disk["type"] == "SSD"]
hdds = [disk for disk in detected_disks if disk["type"] == "HDD"]

# Create input fields for SSD specifications
# Select SSD
#selected_ssd_index = st.selectbox("Select SSD:", options=range(len(disks)), format_func=lambda x: f"SSD {x + 1}")
# Auto-fill input fields based on the selected SSD
#selected_ssd = disks[selected_ssd_index]
#ssd_capacity = st.number_input("Enter SSD Capacity (GB):", min_value=1, value=int(math.ceil(selected_ssd["size_GB"])))
#ssd_manufacturer = st.text_input("Enter SSD Manufacturer:", value=selected_ssd["manufacturer"])
#ssd_capacity = st.number_input("Enter SSD Capacity (GB):", min_value=1, value=200)
#ssd_manufacturer = st.text_input("Enter SSD Manufacturer:", value="Samsung")
if ssds:
    # Select SSD
    selected_ssd_index = st.selectbox("Select SSD:", options=range(len(ssds)), format_func=lambda x: f"SSD {x + 1}")
    selected_ssd = ssds[selected_ssd_index]
    ssd_capacity = st.number_input("Enter SSD Capacity (GB):", min_value=1, value=int(selected_ssd["size_GB"]))
    ssd_manufacturer = st.text_input("Enter SSD Manufacturer:", value=selected_ssd["manufacturer"])

    if st.button("Fetch SSD Data"):
        try:
            ssd_payload = {
                "capacity": ssd_capacity,
                "manufacturer": ssd_manufacturer,
            }
            response = requests.post("http://backend:8000/SSD-Calc", json=ssd_payload)
            response.raise_for_status()
            ssd_data = response.json()

            st.subheader("SSD Impact Information:")
            impacts = ssd_data.get("impacts", {})
            impact_keys = list(impacts.keys())[:6]
            for key in impact_keys:
                impact_info = impacts[key]
                st.text(f"{key.upper()}")
                st.text(f"Description: {impact_info['description']}")
                st.text(f"Unit: {impact_info['unit']}")
                st.text(f"Embedded Value: {impact_info['embedded']['value']} {impact_info['unit']}")
                st.text("")  # Add a line break

        except requests.RequestException as e:
            st.error(f"Failed to retrieve SSD data: {str(e)}")
else:
    st.info("No SSDs detected in the system information.")


st.subheader("Boavizta HDD Calculations", divider = True)

if hdds:
    # Select HDD
    selected_hdd_index = st.selectbox("Select HDD:", options=range(len(hdds)), format_func=lambda x: f"HDD {x + 1}")
    selected_hdd = hdds[selected_hdd_index]
    hdd_capacity = st.number_input("Enter HDD Capacity (GB):", min_value=1, value=int(selected_hdd["size_GB"]))
    hdd_units = st.number_input("Enter HDD units:", min_value=1, value=1)

    if st.button("Fetch HDD Data"):
        try:
            hdd_payload = {
                "units": hdd_units,
                "type": "HDD",
                "capacity": hdd_capacity,
            }
            response = requests.post("http://backend:8000/HDD-Calc", json=hdd_payload)
            response.raise_for_status()
            hdd_data = response.json()

            st.subheader("HDD Impact Information:")
            impacts = hdd_data.get("impacts", {})
            impact_keys = list(impacts.keys())[:6]
            for key in impact_keys:
                impact_info = impacts[key]
                st.text(f"{key.upper()}")
                st.text(f"Description: {impact_info['description']}")
                st.text(f"Unit: {impact_info['unit']}")
                st.text(f"Embedded Value: {impact_info['embedded']['value']} {impact_info['unit']}")
                st.text("")  # Add a line break

        except requests.RequestException as e:
            st.error(f"Failed to retrieve HDD data: {str(e)}")
else:
    st.info("No HDDs detected in the system information.")

# Select HDD with a filter for HDD type only
#filtered_hdds = [disk for disk in disks if disk["type"] == "HDD"]
#selected_hdd_index = st.selectbox("Select HDD:", options=range(len(filtered_hdds)), format_func=lambda x: f"HDD {x + 1}")


# Create input fields for SSD specifications
#hdd_units = st.number_input("Enter HDD units :" , min_value =1)
#hdd_capacity = st.number_input("Enter HDD Capacity (GB): (Not Necessary)", min_value=1)
#hdd_type = "HDD"
# Auto-fill input fields based on the selected HDD
#selected_hdd = filtered_hdds[selected_hdd_index]
#hdd_capacity = st.number_input("Enter HDD Capacity (GB):", min_value=1, value=int(math.ceil((selected_hdd["size_GB"]))))
#hdd_units = st.number_input("Enter HDD units:", min_value=1, value=1)
#left, middle, right = st.columns(3)
#if right.button("Fetch HDD Data"):
#    # HTTP POST request with inputs to FastAPI endpoint
#    try:
#        payload = {
#            "units" : hdd_units,
#            "type" : hdd_type,
#            "capacity": hdd_capacity,        }
#        response = requests.post("http://backend:8000/HDD-Calc", json=payload)
#        response.raise_for_status()  # Raise error for bad responses
#        hdd_data = response.json()
#
#        # Display the first 6 impact entries
#        st.subheader("Impact Information:")
#
#        impacts = hdd_data.get("impacts", {})
#        impact_keys = list(impacts.keys())[:6]  # Get the first 6 keys
#
#        for key in impact_keys:
#            impact_info = impacts[key]
#            st.text(f"{key.upper()}")
#            st.text(f"Description: {impact_info['description']}")
#            st.text(f"Unit: {impact_info['unit']}")
#            st.text(f"Embedded Value: {impact_info['embedded']['value']} {impact_info['unit']}")
#           # st.text(f"Using value: {impact_info['use']['value']} {impact_info['unit']}")
#
#            st.text("")  # Add a line break
#
#    except requests.RequestException as e:
#        st.error(f"Failed to retrieve RAM data: {str(e)}")


st.title("Server Case Scope3 Calculation")

st.subheader("Boavizta Case Calculations", divider = True)

# Create input fields for SSD specifications
case_type = st.selectbox("Case Type :", ("blade", "rack"),)
left, middle, right = st.columns(3)

if right.button("Fetch Case Data"):
    # HTTP POST request with inputs to FastAPI endpoint
    try:
        payload = {
            "case_type": case_type,
        }
        response = requests.post("http://backend:8000/Case-Calc", json=payload)
        response.raise_for_status()  # Raise error for bad responses
        case_data = response.json()

        # Display the first 6 impact entries
        st.subheader("Impact Information:")

        impacts = case_data.get("impacts", {})
        impact_keys = list(impacts.keys())[:6]  # Get the first 6 keys

        for key in impact_keys:
            impact_info = impacts[key]
            st.text(f"{key.upper()}")
            st.text(f"Description: {impact_info['description']}")
            st.text(f"Unit: {impact_info['unit']}")
            st.text(f"Embedded Value: {impact_info['embedded']['value']} {impact_info['unit']}")
           # st.text(f"Using value: {impact_info['use']['value']} {impact_info['unit']}")

            st.text("")  # Add a line break

    except requests.RequestException as e:
        st.error(f"Failed to retrieve Case data: {str(e)}")

st.title("Motherboard Scope3 Calculation (API non functional)")

st.subheader("Boavizta Motherboard Calculations", divider = True)

motherboard_units = st.number_input("Enter Motherboaerd units:", min_value = 1, value = 1)
motherboard_gwp = 66.10
motherboard_adp = 3.69E-03
motherboard_pe  = 836.00

left, middle, right = st.columns(3)

if right.button("Calculate Motherboard Impact"):

    st.text(f"Motherboard GWP : {motherboard_units * motherboard_gwp} kgCO2eq")
    st.text(f"Motherboard ADP :  {motherboard_units * motherboard_adp} kgSbeq")
    st.text(f"Motherboard PE :  {motherboard_units * motherboard_pe} MJ")

st.title("GPU Scope3 Calculation (API non Present)")

st.subheader("Boavizta GPU Calculations", divider = True,      help="Based on formula found in the following article: https://hal.science/hal-04643414v1/document")

gpus = [gpu for gpu in detected_GPU]


if gpus:
    # Select GPU
    selected_gpu_index = st.selectbox("Select GPU:", options=range(len(gpus)), format_func=lambda x: f"GPU {x + 1}")
    selected_gpu = gpus[selected_gpu_index]
    gpu_brand = st.text_input("GPU Model", value=selected_gpu)

    database = GPUDatabase.default()
    try:
        # Search for GPU specifications locally
        spec = database.search(gpu_brand)
        die_size = spec.die_size_mm2
        ram_size = spec.memory_size_gb
    except KeyError:
        st.error(f"Could not find specifications for GPU: {gpu_brand}")
        die_size = 0.1  # Set default to avoid input errors
        ram_size = 1

    die_size_input = st.number_input("GPU Die Size (mm²)", format="%.2f", value=die_size)
    ram_size_input = st.number_input("RAM Size (GB)", value=ram_size)

    if st.button("Calculate GPU Impact"):
        if gpu_brand and die_size > 0 and ram_size > 0:
            # Assume there's a Calculate_GPU_impact function that requires these values
            gpu_impacts = Calculate_GPU_impact(die_size, ram_size)
            st.success(f"Calculations for {gpu_brand}:")
            st.text(f"GPU GWP: {gpu_impacts[0]:.2f} kgCO2eq")
            st.text(f"GPU ADP: {gpu_impacts[1]:.2e} kgSbeq")
            st.text(f"GPU PE: {gpu_impacts[2]:.2f} MJ")
        else:
            st.warning("Please provide all required inputs.")
else:
    st.info("No GPUs detected in the system information.")


st.title("Power and Carbon")

### Display Power Breakdown

try:
    # Fetch data from FastAPI backend
    response = requests.get(f"{FASTAPI_BASE_URL}/power-breakdown?zone=FR")
    response.raise_for_status()
    data = response.json()

    st.subheader('Electricity Maps Live Power Breakdown')
    st.subheader(f"Zone: {data.get('zone', 'N/A')}")

    # Extract breakdown data
    breakdown = data.get('powerProductionBreakdown', {})
    df_elec = pd.DataFrame(breakdown.items(), columns=["Source", "Power (MW)"])

    # Display JSON breakdown
    #st.json(breakdown)

    # Create pie chart
    fig = px.pie(df_elec, values='Power (MW)', names='Source', title="Energy Production Breakdown")
    st.plotly_chart(fig)
except Exception as e:
    st.error(f"Failed to fetch power breakdown data: {e}")

### Display Carbon Intensity

try:
    # Fetch data from FastAPI backend
    response_carbon = requests.get(f"{FASTAPI_BASE_URL}/carbon-intensity?zone=FR")
    response_carbon.raise_for_status()
    data_carbon = response_carbon.json()

    st.subheader('Electricity Maps Live Carbon Intensity')
    st.subheader(f"Zone: {data_carbon.get('zone', 'N/A')}")

    # Display JSON data
    st.json(data_carbon)

    # Optional: Visualize carbon intensity data if applicable
    df_carbon = pd.DataFrame(data_carbon.items(), columns=['Metric', 'Value'])
    st.write(df_carbon)
except Exception as e:
    st.error(f"Failed to fetch carbon intensity data: {e}")


