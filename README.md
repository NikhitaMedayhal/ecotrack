EcoTrack

EcoTrack is a lightweight real-time network monitoring and carbon estimation system that quantifies the environmental impact of digital activity at the device level.

It passively captures network throughput, estimates associated energy consumption, and computes approximate CO₂ emissions using standardized intensity models.

Built for GENESYS 2.0 – Green Computing Hackathon.

---

1. System Architecture

EcoTrack follows a modular pipeline:

Network Interface Layer  
        ↓  
Usage Sampling Engine  
        ↓  
Carbon Estimation Engine  
        ↓  
Analytics Layer  
        ↓  
Visualization Dashboard  

---

2. Core Components

2.1 Network Monitoring Layer

- Uses `psutil.net_io_counters()`
- Samples total bytes sent/received at fixed intervals
- Computes delta usage over time window
- Converts raw bytes → MB → GB

Sampling Interval: Configurable (default: 5 seconds)

---

2.2 Carbon Estimation Engine

Data usage is converted using a two-step model:

Energy Estimation:

Energy (kWh) = Data (GB) × Energy Intensity (kWh/GB)

Carbon Estimation:

CO₂ (kg) = Energy (kWh) × Grid Carbon Intensity (kgCO₂/kWh)

Default constants (modifiable):
- Energy intensity ≈ 0.06 kWh per GB
- Grid carbon intensity ≈ 0.475 kg CO₂ per kWh

These values can be parameterized for regional adaptation.

---

2.3 Activity Classification (Heuristic Model)

EcoTrack implements a lightweight classification model based on network throughput patterns:

- Sustained high bandwidth → Streaming
- Sharp throughput spike → Download
- Low steady throughput → Browsing

This avoids deep packet inspection and ensures:
- Low computational overhead
- No content-level privacy intrusion

---

2.4 Data Logging

All processed metrics are appended to structured CSV logs:

Fields include:
- Timestamp
- Bytes sent
- Bytes received
- MB used
- Throughput (MB/s)
- Energy (kWh)
- CO₂ (kg)
- Activity label

---

2.5 Analytics Layer

Uses:
- pandas
- numpy

Computes:
- Cumulative emissions
- Time-series emission trends
- Activity distribution
- Carbon budget comparison
- Eco score

---

2.6 Visualization

Implemented using Streamlit:

- Real-time dashboard
- Metric summaries
- Time-series plots
- Activity breakdown charts
- Budget alerts

---

3. Design Principles

- Passive monitoring
- No packet content inspection
- Low resource overhead
- Modular architecture
- Transparent conversion model
- Configurable emission factors

---

4. Privacy Considerations

EcoTrack:
- Does not store browsing history
- Does not inspect packet payload
- Only records aggregate throughput metrics

---

5. Installation

git clone https://github.com/NikhitaMedayhal/ecotrack 
cd ecotrack
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

---

6. Execution

To start the monitoring engine run: 
python3 logger.py

To launch dashboard:
streamlit run dashboard.py

---
