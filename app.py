import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from streamlit_autorefresh import st_autorefresh
import os

LOG_FILE = "data/ecotrack_log.csv"
ACTIVITY_FILE = "data/activity_state.txt"

st.set_page_config(page_title="EcoTrack", layout="wide")
st.title("🌍 EcoTrack - Digital Carbon Footprint Monitor")
st.markdown("Real-time monitoring of your internet carbon emissions.")
st.markdown("---")

# ---------------- Sidebar: activity tag ----------------
os.makedirs("data", exist_ok=True)

st.sidebar.header("🎯 Tag your current activity")
activity = st.sidebar.radio(
    "What are you doing right now?",
    ["Browsing", "Streaming", "Downloading"],
    index=0
)

# write current activity so logger can read it
with open(ACTIVITY_FILE, "w") as f:
    f.write(activity.lower())

st.sidebar.caption("Saved ✅ (new log entries will be tagged)")

# ---------------- Load data ----------------
def load_data():
    try:
        return pd.read_csv(LOG_FILE)
    except Exception:
        return pd.DataFrame()

# Auto refresh every 5 seconds
st_autorefresh(interval=5000, key="ecotrack_refresh")

df = load_data()

if df.empty:
    st.info("Waiting for data...")
    st.stop()

latest = df.iloc[-1]

# ---------------- Metrics ----------------
col1, col2, col3 = st.columns(3)
col1.metric("Latest CO₂ Emission (g)", round(float(latest["co2_kg"]) * 1000, 3))
col2.metric("Data Used (GB)", round(float(latest["data_gb"]), 5))
col3.metric("Energy Used (kWh)", round(float(latest["energy_kwh"]), 5))

st.write("")

# ---------------- Trend ----------------
st.subheader("📈 Carbon Emission Trend")
st.line_chart(df["co2_kg"] * 1000)

st.write("")

# --- PIE CHART: CO₂ BY ACTIVITY ---
st.subheader("🥧 CO₂ Distribution by Activity")

if "activity" not in df.columns:
    st.warning("No 'activity' column found. Restart the logger after updating it and delete the old CSV once.")
else:
    # total CO₂ per activity (in grams)
    activity_totals = (
        df.groupby("activity")["co2_kg"]
        .sum()
        .sort_values(ascending=False)
        * 1000
    )

    labels = [str(x).title() for x in activity_totals.index.tolist()]
    values = activity_totals.values

    fig, ax = plt.subplots(figsize=(7, 7))
    wedges, _ = ax.pie(values, startangle=90)
    ax.axis("equal")

    ax.legend(
        wedges,
        [f"{labels[i]}: {values[i]:.2f} g" for i in range(len(labels))],
        title="Activity",
        loc="center left",
        bbox_to_anchor=(1.1, 0.5)
    )

    plt.tight_layout()
    st.pyplot(fig, use_container_width=True)

while True:
    #creating an infinite loop
    df = load_data()  #reading the csv made by logger.py
    
    with placeholder.container(): #value given by this loop is given to placeholder    #keeps replacing the old value in placeholder with new value
        if not df.empty:
            latest = df.iloc[-1]

    # Latest metrics
            st.metric("Latest CO₂ (g)", round(latest["co2_kg"] * 1000, 3))

    # Totals
            total_co2 = df["co2_kg"].sum() * 1000
            total_data = df["data_gb"].sum()
            total_energy = df["energy_kwh"].sum()

            col1, col2, col3 = st.columns(3)
            col1.metric("Total CO₂ (g)", round(total_co2, 2))
            col2.metric("Total Data (GB)", round(total_data, 3))
            col3.metric("Total Energy (kWh)", round(total_energy, 4))

    # 🔥 CALL FUNCTION HERE
            st.subheader("💡 Smart Insight")
            st.success(generate_insight(total_co2))

        '''if not df.empty:
            latest = df.iloc[-1] 
            st.metric("Latest CO₂ Emission (g)", round(latest["co2_kg"] * 1000, 3))
            st.metric("Data Used (GB)", round(latest["data_gb"], 5))
            st.metric("Energy Used (kWh)", round(latest["energy_kwh"], 5))
            st.line_chart(df["co2_kg"] * 1000) #
        else:
            st.write("Waiting for data...")
    time.sleep(5)
    total_co2 = df["co2_kg"].sum() * 1000
    st.subheader("💡 Smart Insight")
    st.success(generate_insight(total_co2))'''

def generate_insight(co2):
    if co2 > 0.05:
        return "High usage detected. Consider reducing HD streaming."
    elif co2 > 0.02:
        return "Moderate usage. Good control!"
    else:
        return "Low impact usage. Keep it up!"

