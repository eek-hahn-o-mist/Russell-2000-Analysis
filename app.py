import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.linear_model import LinearRegression

# Page configuration
st.set_page_config(page_title="Corpay Corp Dev Analytics", layout="wide")

st.title("Corpay Corporate Development Hub")
st.subheader("Part 1: Russell 2000 B2B Spend Forecast & Segment Selection Matrix")

# --- 1. HARDCODED SYNTHESIZED DATASET ---
# Data represents middle-market proxy spend volumes and macroeconomic variables
@st.cache_data
def load_russell_data():
    segments = ["Healthcare", "Manufacturing", "Professional Services", "Logistics/Wholesale", "Construction"]
    years = [2023, 2024, 2025]
    
    data_list = []
    
    # Synthesized raw historical matrices
    raw_history = {
        "Healthcare": {"spend": [45.2, 48.5, 52.1], "margin_comp": 3.4, "xb_exposure": 12.0},
        "Manufacturing": {"spend": [68.0, 71.2, 73.8], "margin_comp": 4.1, "xb_exposure": 28.0},
        "Professional Services": {"spend": [32.1, 35.8, 39.5], "margin_comp": 1.8, "xb_exposure": 18.0},
        "Logistics/Wholesale": {"spend": [55.0, 59.4, 64.2], "margin_comp": 5.2, "xb_exposure": 35.0},
        "Construction": {"spend": [40.5, 42.1, 43.8], "margin_comp": 2.5, "xb_exposure": 8.0}
    }
    
    # Macro trends
    ai_maus_growth = {2023: 1.2, 2024: 3.5, 2025: 7.8}
    inflation_rates = {2023: 4.1, 2024: 3.2, 2025: 2.6}

    for idx, seg in enumerate(segments):
        for i, yr in enumerate(years):
            data_list.append({
                "Segment": seg,
                "Year": yr,
                "Non_Salary_Spend_B": raw_history[seg]["spend"][i],
                "AI_MAUs_M": ai_maus_growth[yr] * (1.2 if seg in ["Professional Services", "Healthcare"] else 0.8),
                "Inflation_Rate": inflation_rates[yr],
                "Margin_Compression": raw_history[seg]["margin_comp"],
                "Cross_Border_Exposure": raw_history[seg]["xb_exposure"]
            })
            
    return pd.DataFrame(data_list)

df = load_russell_data()

# --- 2. FORECASTING & LINEAR REGRESSION LOGIC ---
forecasted_data = []
segments = df["Segment"].unique()

for seg in segments:
    seg_df = df[df["Segment"] == seg]
    
    # Train regression on Years -> Spend
    X = seg_df[["Year"]].values
    y = seg_df["Non_Salary_Spend_B"].values
    
    model = LinearRegression()
    model.fit(X, y)
    
    # Predict 2026 and 2027
    future_years = np.array([[2026], [2027]])
    predictions = model.predict(future_years)
    
    # Append historical records
    for _, row in seg_df.iterrows():
        forecasted_data.append({
            "Segment": seg, "Year": int(row["Year"]), "Spend_B": row["Non_Salary_Spend_B"],
            "Type": "Historical", "Margin_Comp": row["Margin_Compression"], "XB_Exposure": row["Cross_Border_Exposure"]
        })
        
    # Append future forecasted records
    for idx, yr in enumerate([2026, 2027]):
        forecasted_data.append({
            "Segment": seg, "Year": yr, "Spend_B": predictions[idx],
            "Type": "Projected", "Margin_Comp":
