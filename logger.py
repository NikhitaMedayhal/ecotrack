from core.monitor import get_network_usage
from core.carbon import bytes_to_gb, gb_to_energy_kwh, energy_to_co2_kg
import csv
import os
from datetime import datetime
from collections import deque

LOG_FILE = "data/ecotrack_log.csv"
HEADER = ["timestamp", "bytes_used", "data_gb", "energy_kwh", "co2_kg", "activity"]

history = deque(maxlen=12)  # last ~1 minute if interval=5s


def ensure_header():
    os.makedirs("data", exist_ok=True)
    if not os.path.exists(LOG_FILE) or os.stat(LOG_FILE).st_size == 0:
        with open(LOG_FILE, "w", newline="") as f:
            csv.writer(f).writerow(HEADER)


def classify_activity(bytes_used, interval_s=5):
    rate_mbps = (bytes_used * 8) / (interval_s * 1_000_000)  # Mbps
    history.append(rate_mbps)

    if len(history) < 4:
        return "browsing"

    avg = sum(history) / len(history)
    peak = max(history)
    burstiness = peak / (avg + 1e-9)

    # Tuneable thresholds
    if avg > 8 and burstiness < 2.0:
        return "streaming"
    if peak > 20 and burstiness >= 2.0:
        return "downloading"
    return "browsing"


ensure_header()

while True:
    bytes_used = get_network_usage(5)

    data_gb = bytes_to_gb(bytes_used)
    energy_kwh = gb_to_energy_kwh(data_gb)
    co2_kg = energy_to_co2_kg(energy_kwh)

    activity = classify_activity(bytes_used, interval_s=5)
    timestamp = datetime.now().isoformat()

    with open(LOG_FILE, "a", newline="") as f:
        csv.writer(f).writerow([timestamp, bytes_used, data_gb, energy_kwh, co2_kg, activity])

    print(f"{timestamp} | {activity} | {co2_kg*1000:.3f} g CO₂")

