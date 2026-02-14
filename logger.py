from core.monitor import get_network_usage
from core.carbon import bytes_to_gb, gb_to_energy_kwh, energy_to_co2_kg
import csv
import os
from datetime import datetime

LOG_FILE = "data/ecotrack_log.csv"

# Write header only if file is empty
def ensure_header():
    if not os.path.exists(LOG_FILE) or os.stat(LOG_FILE).st_size == 0:
        with open(LOG_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "timestamp",
                "bytes_used",
                "data_gb",
                "energy_kwh",
                "co2_kg"
            ])

ensure_header()

while True:
    bytes_used = get_network_usage(5)

    data_gb = bytes_to_gb(bytes_used)
    energy = gb_to_energy_kwh(data_gb)
    co2 = energy_to_co2_kg(energy)

    timestamp = datetime.now().isoformat()

    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            timestamp,
            bytes_used,
            data_gb,
            energy,
            co2
        ])

    print(f"{timestamp} | {co2*1000:.3f} g CO₂")
