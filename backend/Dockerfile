FROM python:3.9-slim



# Install necessary packages
RUN apt-get update && \
    apt-get install -y lshw && \
    apt-get install -y dmidecode && \
    apt-get clean

# Install procps package for the 'free' command and any other dependencies
#RUN apt-get update && apt-get install -y \
#    procps \
#    wget \
#    unzip \
#    chromium \
#    chromium-driver \
#    && apt-get clean \
#    && rm -rf /var/lib/apt/lists/*

# Set display port to avoid crashes
#ENV DISPLAY=:99


# Install necessary packages
RUN apt-get update && apt-get install -y git wget gawk sed curl lshw stress-ng htop
RUN apt-get update && apt-get install -y freeipmi-tools 
RUN apt-get update && apt-get install -y sudo util-linux

# Install dependencies
#RUN apt-get update && apt-get install -y \
#    wget unzip curl gnupg2 \
#    chromium chromium-driver

# Set environment variables for Selenium
#ENV CHROME_BIN=/usr/bin/chromium
#ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

WORKDIR /app

# Download and set up Energizta script
RUN wget https://raw.githubusercontent.com/Boavizta/Energizta/main/energizta/energizta.sh && \
    chmod +x energizta.sh

COPY requirements.txt .
#COPY . .
RUN pip install --no-cache-dir -r requirements.txt
#RUN pip install -r requirements.txt

# Install dbgpu or other necessary packages
#RUN pip install dbgpu[all]

#COPY app/main.py ./app/
COPY . .

EXPOSE 8000

#CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
CMD ["sh", "-c", "echo 'CPU Information:' && cat /proc/cpuinfo && echo 'RAM Information:' && lshw -short && echo 'Disk Information:' && df -h && exec uvicorn app.main:app --host 0.0.0.0 --port 8000"]