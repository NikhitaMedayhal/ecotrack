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
    
    with placeholder.container():   #value given by this loop is given to placeholder    #keeps replacing the old value in placeholder with new value
        if not df.empty:
            latest = df.iloc[-1] 
            st.metric("Latest CO₂ Emission (g)", round(latest["co2_kg"] * 1000, 3))
            st.metric("Data Used (GB)", round(latest["data_gb"], 5))
            st.metric("Energy Used (kWh)", round(latest["energy_kwh"], 5))
            st.line_chart(df["co2_kg"] * 1000) #
        else:
            st.write("Waiting for data...")
    time.sleep(5)
def generate_insight(co2):
    if co2 > 0.05:
        return "High usage detected. Consider reducing HD streaming."
    elif co2 > 0.02:
        return "Moderate usage. Good control!"
    else:
        return "Low impact usage. Keep it up!"
