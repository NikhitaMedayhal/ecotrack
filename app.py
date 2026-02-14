import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from streamlit_autorefresh import st_autorefresh

LOG_FILE = "data/ecotrack_log.csv"

st.set_page_config(page_title="EcoTrack", layout="wide")
st.title("🌍 EcoTrack - Digital Carbon Footprint Monitor")
st.markdown("Real-time monitoring of your internet carbon emissions.")
st.markdown("---")


def load_data():
    try:
        return pd.read_csv(LOG_FILE)
    except Exception:
        return pd.DataFrame()


def generate_insight(co2_g):
    if co2_g > 50:  # grams
        return "High usage detected. Consider reducing HD streaming."
    elif co2_g > 20:
        return "Moderate usage. Good control!"
    else:
        return "Low impact usage. Keep it up!"


# Auto refresh every 5 seconds
st_autorefresh(interval=5000, key="ecotrack_refresh")

df = load_data()

if df.empty:
    st.info("Waiting for data...")
    st.stop()

latest = df.iloc[-1]

# Sidebar: show detected activity (only after df exists)
if "activity" in df.columns:
    st.sidebar.success(f"Detected: {str(latest['activity']).title()}")
else:
    st.sidebar.info("Activity column not found (update logger & restart logging).")

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

# ---------------- Insight ----------------
total_co2_g = float(df["co2_kg"].sum() * 1000)
st.subheader("💡 Smart Insight")
st.success(generate_insight(total_co2_g))

st.write("")

# ---------------- Pie chart ----------------
st.subheader("🥧 CO₂ Distribution by Activity")

if "activity" not in df.columns:
    st.warning("No 'activity' column found. Delete old CSV, restart logger, then refresh.")
else:
    activity_totals = (
        df.groupby("activity")["co2_kg"]
        .sum()
        .sort_values(ascending=False)
        * 1000
    )

    # guard: if everything is empty / NaN
    if activity_totals.empty:
        st.info("No activity data yet. Let the logger run a bit.")
    else:
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

