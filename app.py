import streamlit as st
import pandas as pd
import numpy as np
import joblib

# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------
# Your model should be trained on:
# y = np.log1p(epi_region["epi_total"])
#
# Then saved from the notebook with:
# joblib.dump(model, "epiphyte_suitability.pkl")

MODEL_PATH = "epiphyte_suitability.pkl"

# Suitability threshold:
# At or above this predicted number of epiphyte species, the app shows 100%.
#
# Based on your dataset:
# 25% = 2 species
# 50% = 6 species
# 75% = 251 species
# max = 5574 species
#
# A threshold of 500 means regions predicted to support around 500+ epiphyte
# species are treated as fully suitable, without letting extreme hotspots
# like 5000+ species dominate the scale.
SUITABILITY_THRESHOLD = 500


# ------------------------------------------------------------
# Helper functions
# ------------------------------------------------------------
def richness_to_percentage(richness, threshold=SUITABILITY_THRESHOLD):
    """
    Convert predicted species richness to a user-friendly suitability percentage.

    Example:
        richness = 250, threshold = 500 -> 50%
        richness = 500, threshold = 500 -> 100%
        richness = 1000, threshold = 500 -> 100%
    """
    richness = max(0, richness)
    percentage = (richness / threshold) * 100
    return max(0, min(100, percentage))


def get_suitability_label(percentage):
    """Return a simple interpretation label."""
    if percentage >= 80:
        return "Very high suitability", "success"
    elif percentage >= 60:
        return "High suitability", "success"
    elif percentage >= 40:
        return "Moderate suitability", "warning"
    elif percentage >= 20:
        return "Low suitability", "warning"
    else:
        return "Very low suitability", "error"


# ------------------------------------------------------------
# Load model
# ------------------------------------------------------------
model = joblib.load(MODEL_PATH)


# ------------------------------------------------------------
# Streamlit page setup
# ------------------------------------------------------------
st.set_page_config(
    page_title="Epiphyte Suitability Predictor",
    page_icon="🌿",
    layout="centered"
)

st.title("🌿 Epiphyte Suitability Predictor")

st.write(
    """
    Enter environmental conditions to estimate how suitable a region is for
    epiphytes.

    The model predicts **epiphyte species richness**, then converts it into a
    percentage using a fixed suitability threshold.
    """
)

st.info(
    f"Current threshold: **{SUITABILITY_THRESHOLD} predicted epiphyte species = 100% suitability**"
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
    min_value=-30.0,
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
    # Model predicts log1p(epi_total)
    log_prediction = model.predict(sample)[0]

    # Convert back to predicted species richness
    predicted_richness = np.expm1(log_prediction)
    predicted_richness = max(0, predicted_richness)

    # Convert richness to threshold-based suitability percentage
    suitability_percentage = richness_to_percentage(predicted_richness)

    label, label_type = get_suitability_label(suitability_percentage)

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            label="Estimated epiphyte richness",
            value=f"{predicted_richness:.0f} species"
        )

    with col2:
        st.metric(
            label="Epiphyte suitability",
            value=f"{suitability_percentage:.1f}%"
        )

    if label_type == "success":
        st.success(label)
    elif label_type == "warning":
        st.warning(label)
    else:
        st.error(label)

    st.write("Input used by the model:")
    st.dataframe(sample)

    st.caption(
        "Suitability is calculated as predicted richness divided by the chosen "
        "threshold, capped at 100%."
    )


# ------------------------------------------------------------
# Notes
# ------------------------------------------------------------
st.divider()

st.caption(
    "Model inputs: absolute latitude, mean annual precipitation, precipitation "
    "seasonality, mean daily minimum temperature, and elevation range. "
    "Model target: log-transformed epiphyte richness using log1p(epi_total)."
)
