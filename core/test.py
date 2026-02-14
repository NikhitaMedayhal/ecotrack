from core.monitor import get_network_usage
from core.carbon import bytes_to_gb, gb_to_energy_kwh, energy_to_co2_kg

while True:
    b = get_network_usage(5)
    gb = bytes_to_gb(b)
    e = gb_to_energy_kwh(gb)
    co2 = energy_to_co2_kg(e)

    print(f"{b} bytes | {gb:.6f} GB | {co2*1000:.3f} g CO₂")


