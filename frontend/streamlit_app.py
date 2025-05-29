import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from backend.electricitymaps import fetch_power_breakdown
from backend.carbon_intensity import fetch_carbon_intensity
import subprocess



def fetch_system_info():
    try:
        response = requests.get("http://backend:8000/system-info")
        response.raise_for_status()
        data = response.json()
        return data.get("system_info", "No data found.")
    except requests.exceptions.RequestException as e:
        return f"Error fetching data: {e}"

st.title("System Information")

system_info = fetch_system_info()
st.text(system_info)


def read_system_info():
    try:
        with open("/output/system_info.txt", "r") as file:
            return file.read()
    except FileNotFoundError:
        return "System information file not found. Please ensure the backend processes are running correctly."
    except Exception as e:
        return f"Error reading system info: {e}"

# Streamlit UI
st.title("System Information")

# Automatically print system information
system_info = read_system_info()
st.text(system_info)



# Function to read the contents of a file
def read_output(file_path):
    try:
        with open(file_path, 'r') as f:
            return f.read()
    except FileNotFoundError:
        return "Output file not found. Please run the command again."
    except Exception as e:
        return f"Error reading file: {e}"

# Title of the app
st.title("System Information")

# Section for Hardware Information
st.header("Hardware Information")
hardware_info = read_output("/output/hardware_info.txt")
st.text(hardware_info)

# Section for Memory Information
st.header("Memory Information")
memory_info = read_output("/output/memory_info.txt")
st.text(memory_info)

# Refresh Actions
if st.button("Refresh Hardware Info"):
    try:
        with open('/hostpipe/mypipe', 'w') as pipe:
            pipe.write("lshw")
        st.success("Lshw command sent successfully.")
    except FileNotFoundError:
        st.error("Named pipe not found. Check Docker volume mounts.")

if st.button("Refresh Memory Info"):
    try:
        with open('/hostpipe/mypipe', 'w') as pipe:
            pipe.write("lsmem")
        st.success("Memory info command sent successfully.")
    except FileNotFoundError:
        st.error("Named pipe not found. Check Docker volume mounts.")

""" def read_output(file_path):
    try:
        with open(file_path, 'r') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"

# Title of the app
st.title("System Information")

# Section for Hardware Information
st.header("Hardware Information")
hardware_info = read_output("/output/hardware_info.txt")  # Adjusting path for Docker
st.text(hardware_info)

# Section for Memory Information
st.header("Memory Information")
memory_info = read_output("/output/memory_info.txt")
st.text(memory_info)

# Section for Command Output
st.header("Output of Other Commands")
command_output = read_output("/output/output.txt")
st.text(command_output)

# Optionally, add a button to run the lshw command
if st.button("Refresh Hardware Info"):
    # Send command to the named pipe
    command_to_send = "lshw"
    with open('/hostpipe/mypipe', 'w') as pipe:
        pipe.write(command_to_send)
    st.success("Running lshw command...") """

""" def get_cpu_info():
    return subprocess.check_output("cat /proc/cpuinfo", shell=True).decode()

def get_ram_info():
    try:
        return subprocess.check_output("lshw -short", shell=True).decode()
    except subprocess.CalledProcessError as e:
        return f"Failed to get hardware info: {e}"

def get_disk_info():
    return subprocess.check_output("df -h", shell=True).decode()

st.title("System Information")

# Fetch and display the CPU information
st.header("CPU Information")
cpu_info = get_cpu_info()
st.write(cpu_info)

# Fetch and display the RAM information
st.header("RAM Information")
ram_info = get_ram_info()
st.write(ram_info)

# Fetch and display the disk information
st.header("Disk Information")
disk_info = get_disk_info()
st.write(disk_info) """

st.title("Streamlit Frontend")

FASTAPI_BASE_URL = "http://backend:8000" 

response = requests.get("http://backend:8000/")

if response.status_code == 200:
    st.write(response.json()["message"])
else:
    st.error("Failed to connect to the backend")


try:
    cpu_name = requests.get("http://boaviztapi:5000/v1/utils/cpu_name", headers={"accept": "application/json"})
    cpu_name.raise_for_status()  # Raise an error for bad responses
    data = cpu_name.json()
    st.write(data)
except requests.RequestException as e:
    st.error(f"Failed to fetch data from Boavizta API: {str(e)}")


st.subheader("Configuration Identification", divider = True)

try:
    config_response = requests.post("http://backend:8000/get-config")
    config_response.raise_for_status()
    config_data = config_response.json()
    
    st.json(config_data)  # Adjust output processing if needed
except requests.RequestException as e:
    st.error(f"Failed to retrieve system configuration: {str(e)}")




st.title("Boavizta CPU Calculation")

st.subheader("CPU Scope3 Calculations", divider = True)



# Create input fields for RAM specifications
cpu_name = st.text_input("Enter CPU Name:", value="intel xeon gold 6134")
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
ram_capacity = st.number_input("Enter RAM Capacity (GB):", min_value=1, max_value=128, value=32)
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

# Create input fields for SSD specifications
ssd_capacity = st.number_input("Enter SSD Capacity (GB):", min_value=1, value=200)
ssd_manufacturer = st.text_input("Enter SSD Manufacturer:", value="Samsung")
left, middle, right = st.columns(3)

if right.button("Fetch SSD Data"):
    # HTTP POST request with inputs to FastAPI endpoint
    try:
        payload = {
            "capacity": ssd_capacity,
            "manufacturer": ssd_manufacturer,
        }
        response = requests.post("http://backend:8000/SSD-Calc", json=payload)
        response.raise_for_status()  # Raise error for bad responses
        ssd_data = response.json()

        # Display the first 6 impact entries
        st.subheader("Impact Information:")

        impacts = ssd_data.get("impacts", {})
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
        st.error(f"Failed to retrieve RAM data: {str(e)}")

st.subheader("Boavizta HDD Calculations", divider = True)

# Create input fields for SSD specifications
hdd_units = st.number_input("Enter HDD units :" , min_value =1)
hdd_capacity = st.number_input("Enter HDD Capacity (GB): (Not Necessary)", min_value=1)
hdd_type = "HDD"
left, middle, right = st.columns(3)
if right.button("Fetch HDD Data"):
    # HTTP POST request with inputs to FastAPI endpoint
    try:
        payload = {
            "units" : hdd_units,
            "type" : hdd_type,
            "capacity": hdd_capacity,        }
        response = requests.post("http://backend:8000/HDD-Calc", json=payload)
        response.raise_for_status()  # Raise error for bad responses
        hdd_data = response.json()

        # Display the first 6 impact entries
        st.subheader("Impact Information:")

        impacts = hdd_data.get("impacts", {})
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
        st.error(f"Failed to retrieve RAM data: {str(e)}")


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

left , right  = st.columns(2)
st.text_input("GPU Brand")
st.number_input("GPU Cores",  min_value = 1)

st.title('Electricity Maps Visualization Dashboard')

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
    st.json(breakdown)

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


