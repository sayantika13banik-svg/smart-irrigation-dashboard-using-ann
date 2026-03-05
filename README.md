# Smart Irrigation & Water Conservation System

An AI-powered irrigation decision system built with **Streamlit** that uses real-time weather data, an **Artificial Neural Network (ANN)**, and **Fuzzy Logic** to recommend whether a crop needs irrigation — helping farmers conserve water smartly.
> **Live Demo:** https://dashboardpy-7zyzxkjj8rh6yu6wfnapwd.streamlit.app
## Screenshot:
<img width="1898" height="899" alt="screenshot1" src="https://github.com/user-attachments/assets/d3e24754-cbc2-4926-b759-93a11dca6904" />
<img width="1886" height="840" alt="screenshot2" src="https://github.com/user-attachments/assets/782a3c9a-71c0-4a6b-b700-1be5514d50bd" />

## How It Works:

- User enters a **city name**, selects **crop type** and **soil type** from the sidebar
-  Live weather data is fetched from the **OpenWeatherMap API**
-  **Soil moisture** is estimated from humidity, rainfall, and temperature
-  **Fuzzy Logic** classifies soil moisture into Dry / Moderate / Wet membership values
-  An **ANN** processes the inputs through a weighted sigmoid function to produce a 0–1 score
-  If the score exceeds 0.5, irrigation is recommended as **ON**, otherwise **OFF**, with reasons shown

## Features

- Live weather metrics — temperature, humidity, wind speed, rainfall (last 1h)
- Rain probability estimation based on weather condition
- ANN-based irrigation decision with output score
- Fuzzy soil moisture classification (Dry / Moderate / Wet) in expandable section
- Supports 6 crop types with individual moisture thresholds
- Supports 3 soil types with threshold adjustments
- Estimated water savings percentage

---

## ANN Model

The irrigation decision uses a single-neuron ANN with sigmoid activation:

```python
Inputs (normalized 0–1):
  T_norm = temperature / 50
  H_norm = humidity / 100
  R_norm = rainfall / 20
  M_norm = estimated_soil_moisture / 100

Weighted Sum:
  Z = (0.35 × T) + (0.20 × H) − (0.50 × R) − (0.60 × M) + 0.10

Sigmoid Output:
  ANN_output = 1 / (1 + e^−Z)

Decision:
  ANN_output > 0.5  →  Irrigation ON
  ANN_output ≤ 0.5  →  Irrigation OFF
```

Higher temperature pushes toward irrigation; recent rainfall and high soil moisture push against it.

---

## Fuzzy Logic — Soil Moisture Classification

```python
Dry      = max(0, min(1, (40 - moisture) / 40))
Moderate = max(0, 1 - abs(moisture - 50) / 20)
Wet      = max(0, min(1, (moisture - 60) / 40))
```

Each value is a membership degree between 0 and 1, shown in the expandable section of the dashboard.

---
  
