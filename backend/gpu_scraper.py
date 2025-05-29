# backend/gpu_scrap.py

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import sqlite3
import time

DB_PATH = "./data/data.db"


def scrape_and_store_gpu_data(db_path=DB_PATH):
    # Set up headless browser
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)

    url = "https://www.techpowerup.com/gpu-specs/?mfgr=NVIDIA&sort=name"
    driver.get(url)
    time.sleep(5)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    table = soup.find("table", {"class": "processors"})
    rows = table.find_all("tr")[1:]

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS gpus (
        name TEXT,
        die_size_mm2 REAL,
        memory_size_gb REAL,
        memory_type TEXT
    )
    """)

    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 10:
            continue
        name = cols[0].text.strip()
        die_size_str = cols[6].text.strip().replace(" mm²", "")
        memory_str = cols[7].text.strip()
        memory_type = cols[8].text.strip()

        try:
            die_size_mm2 = float(die_size_str) if die_size_str else None
            memory_size_gb = float(memory_str.replace("GB", "").strip()) if "GB" in memory_str else None
        except ValueError:
            continue

        cursor.execute("INSERT INTO gpus (name, die_size_mm2, memory_size_gb, memory_type) VALUES (?, ?, ?, ?)",
                       (name, die_size_mm2, memory_size_gb, memory_type))

    conn.commit()
    conn.close()
