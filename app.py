import streamlit as st
import pandas as pd
import joblib

# Load model
model = joblib.load("epiphyte_suitability.pkl")

st.set_page_config(
    page_title="Epiphyte Compatibility Predictor",
    page_icon="🌿",
    layout="centered"
)

st.title("🌿 Epiphyte Compatibility Predictor")

st.write(
    """
    Enter environmental conditions and estimate how suitable
    they are for epiphytes.
    """
)

# Inputs

biome = st.selectbox(
    "Biome",
    [
        "Temperate Broadleaf & Mixed Forests",
        "Tropical & Subtropical Moist Broadleaf Forests",
        "Deserts & Xeric Shrublands",
        "Tropical & Subtropical Grasslands, Savannas & Shrublands",
        "Temperate Grasslands, Savannas & Shrublands",
        "Boreal Forests/Taiga",
        "Mediterranean Forests, Woodlands & Scrub",
        "Temperate Conifer Forests",
        "Tundra",
        "Montane Grasslands & Shrublands",
        "Tropical & Subtropical Dry Broadleaf Forests",
        "Tropical & Subtropical Coniferous Forests"
    ]
)

temp_mean = st.slider(
    "Mean Daily Minimum Temperature (°C)",
    -20.0,
    35.0,
    20.0
)

prec = st.slider(
    "Annual Precipitation (mm)",
    0,
    10000,
    2500
)

prec_seas = st.slider(
    "Precipitation Seasonality",
    0,
    300,
    50
)

elev_range = st.slider(
    "Elevation Range (m)",
    0,
    8000,
    2000
)

# Prediction

if st.button("Predict Compatibility"):

    sample = pd.DataFrame({
        "biome": [biome],
        "prec": [prec],
        "PrecSeas": [prec_seas],
        "temp_mean": [temp_mean],
        "ElevRange": [elev_range]
    })

    prediction = model.predict(sample)[0]

    prediction = max(0, min(1, prediction))

    st.success(
        f"Epiphyte Compatibility: {prediction * 100:.1f}%"
    )

    if prediction > 0.8:
        st.write("Excellent conditions for epiphytes.")
    elif prediction > 0.6:
        st.write("Good conditions for epiphytes.")
    elif prediction > 0.4:
        st.write("Moderate suitability.")
    else:
        st.write("Low suitability for epiphytes.")