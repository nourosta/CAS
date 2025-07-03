#!/bin/bash

# Run the system info collection script
#bash /home/nour/phd_proto/week2/scripts/collect_system_info.sh
bash "$(dirname "$0")/scripts/collect_system_info.sh"

# Define location of the output file
SYSTEM_INFO_FILE="$HOME/system_info.txt"

# Check if the file exists
if [[ -f "$SYSTEM_INFO_FILE" ]]; then
    # Extract information using grep and cut
    CPU_NAME=$(grep "CPU Name:" "$SYSTEM_INFO_FILE" | cut -d ':' -f 2 | xargs)
    TOTAL_RAM=$(grep "Total RAM:" "$SYSTEM_INFO_FILE" | cut -d ':' -f 2 | xargs)
    DISK_INFO=$(grep "SSD" "$SYSTEM_INFO_FILE" | xargs)
    GPU_INFO=$(grep "GPU:" "$SYSTEM_INFO_FILE" | cut -d ':' -f 2 | xargs)

    # Export environment variables
    export CPU_NAME
    export TOTAL_RAM
    export DISK_INFO
    export GPU_INFO
else
    echo "System info file not found. Exiting..."
    exit 1
fi

# Start Docker Compose
docker compose up --build
