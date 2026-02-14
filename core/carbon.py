#fixed constants for depiction
KWH_PER_GB = 0.06          # energy intensity (kWh per GB transferred)
KG_CO2_PER_KWH = 0.475     # carbon intensity (kg CO2 per kWh)

def bytes_to_gb(b: int) -> float:
    return b / (1024 ** 3)

def gb_to_energy_kwh(gb: float) -> float:
    return gb * KWH_PER_GB

def energy_to_co2_kg(energy_kwh: float) -> float:
    return energy_kwh * KG_CO2_PER_KWH

