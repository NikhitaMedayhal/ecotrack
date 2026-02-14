import streamlit as st
import pandas as pd
import time
LOG_FILE = "data/ecotrack_log.csv"
st.set_page_config(page_title="EcoTrack", layout="wide")
st.title("EcoTrack - By Ecoders!")
st.markdown("Your digital carbon tracker....")

def load_data():
    try:
        df = pd.read_csv(LOG_FILE)
        return df
    except:
        return pd.DataFrame()

placeholder = st.empty() #for updation of carbon values

while True:
    df = load_data()
    
    with placeholder.container():
        if not df.empty:
            latest = df.iloc[-1] 
            st.metric("Latest CO₂ Emission (g)", round(latest["co2_kg"] * 1000, 3))
            st.metric("Data Used (GB)", round(latest["data_gb"], 5))
            st.metric("Energy Used (kWh)", round(latest["energy_kwh"], 5))
            st.line_chart(df["co2_kg"] * 1000)
        else:
            st.write("Waiting for data...")
    time.sleep(5)
