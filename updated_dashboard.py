import streamlit as st
import requests
from datetime import datetime
import math
import matplotlib.pyplot as plt

st.set_page_config(page_title="Smart Irrigation & Water Conservation System", layout="wide")

st.title("Smart Irrigation & Water Conservation System")
st.subheader("Real-time, Weather-aware, ANN-based Irrigation Decision System")
st.write("---")

# Sidebar inputs
st.sidebar.header("Location Settings")
city = st.sidebar.text_input("Enter City Name", "Mumbai")

API_KEY = "YOUR_OPENWEATHER_API_KEY"
api_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"

response = requests.get(api_url).json()
if response.get("cod") != 200:
    st.error("Invalid city name or API error.")
else:
    temperature = response["main"]["temp"]
    humidity = response["main"]["humidity"]
    weather = response["weather"][0]["main"]
    rain = response.get("rain", {}).get("1h", 0)
    wind_speed = response["wind"]["speed"]

    estimated_soil_moisture = max(0, min(humidity + (rain * 20) - (temperature * 0.5), 100))

    st.sidebar.header("Crop & Soil Settings")
    soil_type = st.sidebar.selectbox("Select Soil Type", ["Sandy", "Loamy", "Clay"])
    crop_type = st.sidebar.selectbox("Select Crop Type", ["Rice", "Wheat", "Cotton", "Tomato"])

    soil_factor = {"Sandy": 10, "Loamy": 0, "Clay": -10}[soil_type]
    crop_thresholds = {"Rice": 60, "Wheat": 40, "Cotton": 45, "Tomato": 55}
    adjusted_moisture_threshold = crop_thresholds[crop_type] + soil_factor

    # -------------------- ANN BLOCK --------------------
    T_norm = temperature / 50
    H_norm = humidity / 100
    R_norm = rain / 20
    M_norm = estimated_soil_moisture / 100

    wT, wH, wR, wM = 0.35, 0.20, -0.50, -0.60
    bias = 0.10

    Z = (wT*T_norm) + (wH*H_norm) + (wR*R_norm) + (wM*M_norm) + bias
    ANN_output = 1 / (1 + math.exp(-Z))

    reasons = []
    if temperature > 35: reasons.append("High temperature increasing water demand")
    if humidity < 40: reasons.append("Low humidity → fast evaporation")
    if rain == 0: reasons.append("No rainfall recently → soil drying")
    if estimated_soil_moisture < adjusted_moisture_threshold: reasons.append("Soil moisture below ideal level")

    if ANN_output > 0.5:
        decision = "ON"
        reason = f"Irrigation Required (ANN={ANN_output:.2f}) — " + " | ".join(reasons)
    else:
        decision = "OFF"
        reason = f"Irrigation NOT Required (ANN={ANN_output:.2f}) — " + " | ".join(reasons)

    # -------------------- UI METRICS --------------------
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Temperature", f"{temperature}°C")
        st.metric("Humidity", f"{humidity}%")
        st.metric("Wind Speed", f"{wind_speed} m/s")
    with col2:
        st.metric("Weather", weather)
        st.metric("Rain (1h)", f"{rain} mm")
        st.metric("Soil Moisture (Est.)", f"{estimated_soil_moisture:.1f}%")
    with col3:
        st.metric("Crop Threshold", f"{adjusted_moisture_threshold}%")
        st.metric("ANN Output", f"{ANN_output:.2f}")
        st.metric("Irrigation Decision", decision)

    st.write("---")

    if decision == "ON":
        st.success(reason)
    else:
        st.error(reason)

    st.write("---")

    fig, ax = plt.subplots()
    ax.bar(["Moisture", "Threshold"], 
           [estimated_soil_moisture, adjusted_moisture_threshold])
    st.pyplot(fig)
