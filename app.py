import streamlit as st
import pandas as pd
import joblib

# ------------------------------------------------------------
# Load trained model
# ------------------------------------------------------------
# This file should be created from your notebook with:
# joblib.dump(model, "epiphyte_suitability.pkl")
MODEL_PATH = "epiphyte_suitability.pkl"

model = joblib.load(MODEL_PATH)

# ------------------------------------------------------------
# Page settings
# ------------------------------------------------------------
st.set_page_config(
    page_title="Epiphyte Suitability Predictor",
    page_icon="🌿",
    layout="centered"
)

st.title("🌿 Epiphyte Suitability Predictor")

st.write(
    """
    This app estimates epiphyte compatibility from environmental conditions.

    The score is a relative suitability percentile based on botanical regions
    in the dataset.
    """
)

# ------------------------------------------------------------
# User inputs
# ------------------------------------------------------------
st.subheader("Environmental conditions")

lat_absolute = st.slider(
    "Absolute latitude (°)",
    min_value=0.0,
    max_value=90.0,
    value=10.0,
    step=0.1,
    help="Distance from the equator. Example: Ecuador ≈ 0°, Heidelberg ≈ 49°."
)

prec = st.number_input(
    "Mean annual precipitation (mm)",
    min_value=0.0,
    max_value=12000.0,
    value=2500.0,
    step=50.0
)

prec_seas = st.number_input(
    "Precipitation seasonality",
    min_value=0.0,
    max_value=300.0,
    value=50.0,
    step=1.0,
    help="Coefficient of variation in precipitation. Higher values mean rainfall is more seasonal."
)

temp_mean = st.number_input(
    "Mean daily minimum temperature (°C)",
    min_value=-20.0,
    max_value=35.0,
    value=20.0,
    step=0.1
)

elev_range = st.number_input(
    "Elevation range (m)",
    min_value=0.0,
    max_value=9000.0,
    value=2000.0,
    step=50.0
)

# ------------------------------------------------------------
# Prediction
# ------------------------------------------------------------
sample = pd.DataFrame({
    "lat_absolute": [lat_absolute],
    "prec": [prec],
    "PrecSeas": [prec_seas],
    "temp_mean": [temp_mean],
    "ElevRange": [elev_range]
})

if st.button("Predict suitability"):
    prediction = model.predict(sample)[0]

    # Keep result inside 0-100%, because models sometimes get ambitious.
    # prediction = max(0.0, min(1.0, prediction))
    # percentage = prediction * 100

    st.metric(
        label="Epiphyte compatibility",
        value=f"{prediction:.1f}%"
    )

    # if percentage >= 80:
    #     st.success("Very high suitability for epiphytes.")
    # elif percentage >= 60:
    #     st.info("Good suitability for epiphytes.")
    # elif percentage >= 40:
    #     st.warning("Moderate suitability for epiphytes.")
    # else:
    #     st.error("Low suitability for epiphytes.")

    st.write("Input used by the model:")
    st.dataframe(sample)

# ------------------------------------------------------------
# Notes
# ------------------------------------------------------------
st.caption(
    "Model inputs: absolute latitude, precipitation, precipitation seasonality, "
    "mean daily minimum temperature, and elevation range."
)
