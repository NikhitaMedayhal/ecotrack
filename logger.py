from core.monitor import get_network_usage
from core.carbon import bytes_to_gb, gb_to_energy_kwh, energy_to_co2_kg
import csv
import os
from datetime import datetime
from collections import deque

history = deque(maxlen=12)  # stores last 12 samples (~1 minute if interval=5s)

def classify_activity(bytes_used, interval_s=5):
    rate_mbps = (bytes_used * 8) / (interval_s * 1_000_000)  # convert to Mbps
    history.append(rate_mbps)

    if len(history) < 4:
        return "browsing"

    avg = sum(history) / len(history)
    peak = max(history)
    burstiness = peak / (avg + 1e-9)

    # You can tweak these thresholds later
    if avg > 8 and burstiness < 2.0:
        return "streaming"

    if peak > 20 and burstiness >= 2.0:
        return "downloading"

    return "browsing"

LOG_FILE = "data/ecotrack_log.csv"
ACTIVITY_FILE = "data/activity_state.txt"

HEADER = ["timestamp", "bytes_used", "data_gb", "energy_kwh", "co2_kg", "activity"]


def ensure_log_file():
    os.makedirs("data", exist_ok=True)

    needs_header = (not os.path.exists(LOG_FILE)) or (os.stat(LOG_FILE).st_size == 0)

    if needs_header:
        with open(LOG_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(HEADER)


def read_activity():
    # default if Streamlit hasn't written anything yet
    try:
        with open(ACTIVITY_FILE, "r") as f:
            a = f.read().strip().lower()
            return a if a else "unknown"
    except:
        return "unknown"


ensure_log_file()

while True:
    bytes_used = get_network_usage(5)
    activity = classify_activity(bytes_used, interval_s=5)

    data_gb = bytes_to_gb(bytes_used)
    energy_kwh = gb_to_energy_kwh(data_gb)
    co2_kg = energy_to_co2_kg(energy_kwh)

    activity = read_activity()
    timestamp = datetime.now().isoformat()

    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, bytes_used, data_gb, energy_kwh, co2_kg, activity])

    print(f"{timestamp} | {activity} | {co2_kg*1000:.3f} g CO₂")

