#!/bin/bash

echo "Collecting System Information..."

# Define output file
#OUTPUT_FILE="$HOME/system_info_nour.txt"
PROJECT_DIR="$(dirname "$0")/../backend/data"
OUTPUT_FILE="$PROJECT_DIR/system_info.txt"

{
    # CPU Information
    echo "=== CPU Information ==="
    cpu_name=$(lscpu | grep "Model name:" | sed 's/Model name:\s*//')
    if [[ -z "$cpu_name" ]]; then
      cpu_name=$(awk -F: '/model name/ {print $2; exit}' /proc/cpuinfo | sed 's/^[ \t]*//')
    fi
    echo "CPU Name: ${cpu_name:-Unknown}"

    echo ""

    # RAM Information
    echo "=== RAM Information ==="
    ram_total_gb=$(awk '/MemTotal/ {printf "%.2f\n", $2/1024/1024}' /proc/meminfo)
    echo "Total RAM: ${ram_total_gb} GB"

    if command -v dmidecode >/dev/null 2>&1; then
      if [ "$(id -u)" -eq 0 ]; then
        echo "RAM Manufacturer(s):"
        dmidecode --type memory | awk -F: '/Manufacturer/ && $2 !~ /Unknown|Not Specified/ {print $2}' | sort | uniq
      else
        echo "Run script as root (sudo) to get RAM manufacturer."
      fi
    else
      echo "dmidecode not installed, skipping RAM manufacturer info."
    fi

    echo ""

    # Disk Storage Information
    echo "=== Disk Storage Information ==="
    echo "Disk devices detected:"
    
    lsblk -d -o NAME,ROTA,SIZE,MODEL | grep -v '^loop' | awk '{
        name=$1; rota=$2; size=$3; model="";
        for(i=4;i<=NF;++i) model=model $i " ";
        type=(rota==0?"SSD":"HDD");
        cmd="udevadm info --query=property --name=/dev/" name " 2>/dev/null";
        vendor="N/A";
        while((cmd | getline line) > 0) {
          if(line ~ /^ID_VENDOR=/) {
            split(line, a, "=");
            vendor=a[2];
          }
        }
        close(cmd);
        printf "%s %s %s %s %s\n", name, type, vendor, model, size;
    }'

    echo ""

    # GPU Information
    echo "=== GPU Information ==="
    if command -v lshw >/dev/null 2>&1; then
        gpu_info=$(lshw -C display | awk -F: '/product:/ {gsub(/^[ \t]+|[ \t]+$/, "", $2); print "GPU: "$2}')
        if [ -z "$gpu_info" ]; then
            echo "No GPU detected."
        else
            echo "$gpu_info"
        fi
    else
        echo "lshw not installed, skipping GPU information."
    fi

    echo ""
    echo "Note: For full RAM manufacturer info, run this script with sudo."
} > "$OUTPUT_FILE"

echo "System information saved to $OUTPUT_FILE"

