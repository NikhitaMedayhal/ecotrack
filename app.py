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
