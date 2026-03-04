import streamlit as st
import requests
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt

st.markdown("""
<style>
.stApp {
    background-color: #131224;
}
[data-testid="stSidebar"] {
    background-color: #1e2036;
}
.card {
    background-color: #1e2036;
    padding: 18px 20px;
    border-radius: 14px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.25);
    color: #f0f0f0;
    transition: 0.2s ease-in-out;
    margin-bottom: 18px; 
    box-shadow: 0px 4px 10px rgba(0,0,0,0.25);
}
.metric-title {
    font-size: 18px;
    font-weight: 600;
    color: #dce3f3;
    margin-bottom: 8px;
}

.metric-value {
    font-size: 28px;
    font-weight: 600;
    color: white;
}
.card:hover {
    transform: translateY(-3px);
    box-shadow: 0 6px 16px rgba(0,0,0,0.35);
}

.card-title {
    font-size: 18px;
    font-weight: 700;
    display: flex;
    align-items: center;
    gap: 8px;
}

.card-sub {
    font-size: 13px;
    opacity: 0.7;
    margin-top: -3px;
}
</style>
""", unsafe_allow_html=True)

st.set_page_config(page_title="Smart Irrigation & Water Conservation System",
                   layout="wide")
st.title("Smart Irrigation & Water Conservation System")

def fuzzy_soil_moisture(moisture):
    dry = max(0, min(1, (40 - moisture) / 40))
    moderate = max(0, 1 - abs(moisture - 50) / 20)
    wet = max(0, min(1, (moisture - 60) / 40))
    return dry, moderate, wet


st.sidebar.header("Input:")

city = st.sidebar.text_input("City:", placeholder="City Name")

soil_type = st.sidebar.selectbox("Select Soil Type", 
                                 ["Sandy", "Loamy", "Clay"])

crop_type = st.sidebar.selectbox("Select Crop Type", 
                                ["Rice", "Wheat", "Cotton", "Tomato", "Flowers", "Sugarcane"])

API_KEY = "d39e920bf70a35b82095eae561f41df2"
api_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"

response = requests.get(api_url).json()

if city.strip() == "":
    st.info("Enter a city name to fetch weather details.")
    st.stop()

if response.get("cod") != 200:
    st.warning("Enter a valid city name.")
    st.stop()

temperature = response["main"]["temp"]
humidity = response["main"]["humidity"]
weather = response["weather"][0]["main"]
rain = response.get("rain", {}).get("1h", 0)
wind_speed = response["wind"]["speed"]

rain_prob = 70 if weather == "Rain" else (40 if weather == "Cloudy" else 10)

estimated_soil_moisture = humidity + (rain * 20) - (temperature * 0.5)
estimated_soil_moisture = max(0, min(estimated_soil_moisture, 100))
dry_m, moderate_m, wet_m = fuzzy_soil_moisture(estimated_soil_moisture)


crop_threshold = {
    "Rice": 60,
    "Wheat": 40,
    "Cotton": 45,
    "Tomato": 55,
    "Flowers": 50,
    "Sugarcane": 65
}[crop_type]


soil_factor = {
    "Sandy": +10,
    "Loamy": 0,
    "Clay": -10
}[soil_type]

adjusted_moisture_threshold = crop_threshold + soil_factor


import math

T_norm = temperature / 50
H_norm = humidity / 100
R_norm = rain / 20
M_norm = estimated_soil_moisture / 100

wT = 0.35   
wH = 0.20     
wR = -0.50  
wM = -0.60
bias = 0.10

Z = (wT*T_norm) + (wH*H_norm) + (wR*R_norm) + (wM*M_norm) + bias

ANN_output = 1 / (1 + math.exp(-Z))

reasons = []

if temperature > 35:
    reasons.append("\nHigh temperature: Crop needs more water")
elif temperature < 20:
    reasons.append("\nLow temperature: Crop needs less water")


if humidity < 40:
    reasons.append("\nLow humidity: Faster evaporation")
elif humidity > 80:
    reasons.append("\nHigh humidity: Slow evaporation")


if rain > 0:
    reasons.append("\nRecent rainfall: Soil may be wet")
else:
    reasons.append("\nNo rainfall: Soil drying faster")


if estimated_soil_moisture < 40:
    reasons.append("\nSoil moisture: Low")
elif estimated_soil_moisture > 70:
    reasons.append("\nSoil moisture: High")

if ANN_output > 0.5:
    decision = "ON"
    reason = (
        f"Irrigation REQUIRED\n\n"
        + "\n".join(reasons)
    )
else:
    decision = "OFF"
    reason = (
        f"Irrigation NOT required\n\n"
        + "\n".join(reasons)
    )



predicted_loss_without_system = 15  
saved_by_rain_prediction = 30 if rain_prob >= 50 else 10
saved_by_timing = 15  

total_savings = predicted_loss_without_system + saved_by_rain_prediction + saved_by_timing



col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
        <div class="card">
        <div class="metric-box">
            <div class="metric-title">Temperature</div>
            <div class="metric-value">{temperature}°C</div>
        </div>

        </div>
        <div class="card">
        <div class="metric-box">
            <div class="metric-title">Humidity</div>
            <div class="metric-value">{humidity}%</div>
        </div>
        </div>
        <div class="card">
        <div class="metric-box">
            <div class="metric-title">Wind Speed</div>
            <div class="metric-value">{wind_speed} m/s</div>
        </div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="card">
        <div class="metric-title">Weather Condition</div>
        <div class="metric-value">{weather}</div>
    </div>

    <div class="card">
        <div class="metric-title">Rain Probability</div>
        <div class="metric-value">{rain_prob}%</div>
    </div>

    <div class="card">
        <div class="metric-title">Rainfall (last 1h)</div>
        <div class="metric-value">{rain} mm</div>
    </div>
    """, unsafe_allow_html=True)


with col3:
    st.markdown(f"""
    <div class="card">
        <div class="metric-title">Est. Soil Moisture</div>
        <div class="metric-value">{round(estimated_soil_moisture, 1)}%</div>
    </div>

    <div class="card">
        <div class="metric-title">Crop Threshold</div>
        <div class="metric-value">{adjusted_moisture_threshold}%</div>
    </div>
    
    <div class="card">
        <div class="metric-title">ANN Output</div>
        <div class="metric-value">{round(ANN_output,2)}</div>
    </div>
    """, unsafe_allow_html=True)

with st.expander("Fuzzy Soil Moisture Classification"):
    st.write(f"**Dry:** {dry_m:.2f}")
    st.write(f"**Moderate:** {moderate_m:.2f}")
    st.write(f"**Wet:** {wet_m:.2f}")



st.write("---")

if decision == "ON":
    st.success(f"**Irrigation: {decision}** — {reason}")
else:
    st.error(f"**Irrigation: {decision}** — {reason}")

st.write("---")

st.subheader("Estimated Water Savings with Smart Irrigation")
st.info(f"Estimated Total Water Saved: **{total_savings}%**")

st.write("---")

