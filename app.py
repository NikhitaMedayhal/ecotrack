import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from streamlit_autorefresh import st_autorefresh
import json
from pathlib import Path
import subprocess
import base64
import io
import math
import wave
import streamlit.components.v1 as components

def play_beep(freq=880, duration=0.18, volume=0.4, sample_rate=44100):
    """Plays a short beep in the browser (works best after 1 user interaction)."""
    n_samples = int(sample_rate * duration)

    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(sample_rate)

        for i in range(n_samples):
            sample = volume * math.sin(2 * math.pi * freq * (i / sample_rate))
            wf.writeframesraw(int(sample * 32767).to_bytes(2, byteorder="little", signed=True))

    b64 = base64.b64encode(buf.getvalue()).decode()
    components.html(
        f"""
        <audio autoplay>
          <source src="data:audio/wav;base64,{b64}" type="audio/wav">
        </audio>
        """,
        height=0,
    )

# ---------------- Paths ----------------
LOG_FILE = "data/ecotrack_log.csv"
ECOGUARD_FILE = Path("data/ecoguard_state.json")
ECOGUARD_FILE.parent.mkdir(parents=True, exist_ok=True)

st.set_page_config(page_title="EcoTrack", layout="wide")

# ---------------- macOS desktop notification ----------------
def send_mac_notification(title: str, message: str):
    """macOS native notification (won't crash app if blocked)."""
    try:
        subprocess.run(
            ["osascript", "-e", f'display notification "{message}" with title "{title}"'],
            check=False
        )
    except Exception as e:
        print("Notification error:", e)

# ---------------- EcoGuard state file (for logger/helper) ----------------
def save_ecoguard(enabled: bool, threshold_g_per_min: float):
    ECOGUARD_FILE.write_text(json.dumps({
        "enabled": enabled,
        "threshold_g_per_min": float(threshold_g_per_min)
    }))

# ---------------- Helpers ----------------
def load_data():
    try:
        return pd.read_csv(LOG_FILE)
    except Exception:
        return pd.DataFrame()

def generate_insight(total_co2_g: float):
    if total_co2_g > 50:
        return "High usage detected. Consider reducing HD streaming."
    elif total_co2_g > 20:
        return "Moderate usage. Good control!"
    else:
        return "Low impact usage. Keep it up!"

def ecoguard_tips(activity: str):
    activity = (activity or "unknown").lower()

    if activity == "streaming":
        return [
            "Lower video quality (1080p → 720p/480p).",
            "Turn off autoplay and background playback.",
            "Prefer downloading once and watching offline."
        ]
    if activity == "downloading":
        return [
            "Pause large downloads and resume later (off-peak).",
            "Avoid re-downloading duplicates.",
            "Compress files before sharing."
        ]
    return [
        "Close unused tabs.",
        "Disable auto-refreshing pages.",
        "Reduce background network activity."
    ]

# ---------------- Session state init ----------------
if "eco_user_enabled" not in st.session_state:
    st.session_state.eco_user_enabled = False
if "eco_auto_enabled" not in st.session_state:
    st.session_state.eco_auto_enabled = False
if "eco_threshold" not in st.session_state:
    st.session_state.eco_threshold = 5.0
if "notified" not in st.session_state:
    st.session_state.notified = False
if "toasted" not in st.session_state:
    st.session_state.toasted = False

# ---------------- Header ----------------
st.title("🌍 EcoTrack - Digital Carbon Footprint Monitor")
st.markdown("Real-time monitoring of your internet carbon emissions.")
st.markdown("---")

# ---------------- Sidebar controls ----------------
st.sidebar.header("🛡️ EcoGuard Mode")

# user-controlled toggle (never write to this key in code!)
st.sidebar.toggle("Enable EcoGuard", key="eco_user_enabled")

# threshold slider
st.sidebar.slider(
    "CO₂ limit (g/min)",
    min_value=0.5,
    max_value=30.0,
    value=float(st.session_state.eco_threshold),
    step=0.5,
    key="eco_threshold"
)

# ---------------- Auto refresh ----------------
st_autorefresh(interval=5000, key="ecotrack_refresh")

# ---------------- Load data ----------------
df = load_data()
if df.empty:
    st.info("Waiting for data...")
    st.stop()

latest = df.iloc[-1]
current_activity = str(latest["activity"]).lower() if "activity" in df.columns else "unknown"

# Sidebar: detected activity
if "activity" in df.columns:
    st.sidebar.success(f"Detected: {current_activity.title()}")
else:
    st.sidebar.info("Activity column not found (update logger & restart).")

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

# ---------------- Current CO₂ rate (g/min) ----------------
df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
df = df.dropna(subset=["timestamp"]).sort_values("timestamp")

window_seconds = 60
cutoff = df["timestamp"].max() - pd.Timedelta(seconds=window_seconds)
df_recent = df[df["timestamp"] >= cutoff]

recent_co2_g = float(df_recent["co2_kg"].sum() * 1000)
recent_rate_g_per_min = (recent_co2_g / window_seconds) * 60

st.metric("Current CO₂ Rate (g/min)", round(recent_rate_g_per_min, 2))

# ---------------- EcoGuard logic (safe with Streamlit widgets) ----------------
threshold = float(st.session_state.eco_threshold)

# auto state (safe to write: NOT a widget key)
st.session_state.eco_auto_enabled = recent_rate_g_per_min > threshold

# final enabled state = user toggle OR auto trigger
eco_enabled = bool(st.session_state.eco_user_enabled or st.session_state.eco_auto_enabled)

# write to file for external components (logger/helper)
save_ecoguard(eco_enabled, threshold)

# messages for auto-activation
if st.session_state.eco_auto_enabled:
    st.warning("⚡ EcoGuard auto-activated due to high CO₂ rate.")

# one-shot toast + notification while "high" (no spam)
if st.session_state.eco_auto_enabled:
    if not st.session_state.toasted:
        st.toast("🛡️ EcoGuard: High CO₂ rate detected! Reduce streaming/downloads.", icon="⚠️")
        st.session_state.toasted = True

    if not st.session_state.notified:
        send_mac_notification(
            "🛡️ EcoGuard Alert",
            f"CO₂ rate {recent_rate_g_per_min:.2f} g/min exceeded limit ({threshold:.2f})."
        )
        st.session_state.notified = True
else:
    # reset one-shot flags when safe again
    st.session_state.toasted = False
    st.session_state.notified = False

# show EcoGuard warning + tips when enabled and above threshold
if eco_enabled and recent_rate_g_per_min > threshold:
    st.error(
        f"🛡️ EcoGuard active: CO₂ rate is above your limit "
        f"({recent_rate_g_per_min:.2f} g/min > {threshold:.2f} g/min)."
    )
    st.markdown("**Try this to reduce impact:**")
    for tip in ecoguard_tips(current_activity):
        st.write("• " + tip)

st.write("")

# ---------------- Pie chart: CO₂ distribution by activity ----------------
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

