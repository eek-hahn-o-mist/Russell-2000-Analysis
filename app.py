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
            "Type": "Projected", "Margin_Comp": seg_df["Margin_Compression"].iloc[0], "XB_Exposure": seg_df["Cross_Border_Exposure"].iloc[0]
        })

df_all = pd.DataFrame(forecasted_data)

# --- 3. SIDEBAR INTERACTIVE CONTROLS ---
st.sidebar.header("Corpay M&A Priority Weights")
st.sidebar.write("Adjust weights to re-rank priority target verticals.")

w_volume = st.sidebar.slider("Spend Volume Weight", 0.0, 1.0, 0.4, 0.1)
w_margin = st.sidebar.slider("Margin Compression Weight", 0.0, 1.0, 0.3, 0.1)
w_xb = st.sidebar.slider("Cross-Border Exposure Weight", 0.0, 1.0, 0.3, 0.1)

# Corpay Unit Economics
st.sidebar.markdown("---")
st.sidebar.subheader("Corpay Unit Economics Input")
take_rate = st.sidebar.number_input("Corpay Net Take Rate (%)", value=0.62, step=0.01) / 100

# --- 4. DATA PRESENTATION & CHARTS ---
col1, col2 = st.columns([2, 1])

with col1:
    st.write("### Historical vs. Projected Spend Volumes ($ Billions)")
    fig = px.bar(df_all, x="Year", y="Spend_B", color="Segment", barmode="group",
                 labels={"Spend_B": "Non-Salary Spend ($B)", "Year": "Fiscal Year"},
                 color_discrete_sequence=px.colors.qualitative.Plotly)  # Updated to official native palette
    st.plotly_chart(fig, use_container_width=True)

# Calculate Attractiveness Score based on 2027 projections
df_2027 = df_all[df_all["Year"] == 2027].copy()

# Max-Min Normalization function for metrics
def normalize(col):
    return (col - col.min()) / (col.max() - col.min()) if (col.max() - col.min()) != 0 else 1.0

df_2027["Norm_Volume"] = normalize(df_2027["Spend_B"])
df_2027["Norm_Margin"] = normalize(df_2027["Margin_Comp"])
df_2027["Norm_XB"] = normalize(df_2027["XB_Exposure"])

# Core algorithm mapping out prioritization scores
df_2027["Attractiveness_Score"] = (
    (df_2027["Norm_Volume"] * w_volume) +
    (df_2027["Norm_Margin"] * w_margin) +
    (df_2027["Norm_XB"] * w_xb)
) * 100

df_2027["Est_Corpay_Addressable_Rev_M"] = (df_2027["Spend_B"] * take_rate) * 1000
summary_df = df_2027[["Segment", "Spend_B", "Margin_Comp", "XB_Exposure", "Attractiveness_Score", "Est_Corpay_Addressable_Rev_M"]].sort_values(by="Attractiveness_Score", ascending=False)

with col2:
    st.write("### Strategic Priorities (2027 View)")
    st.dataframe(summary_df.style.format({
        "Spend_B": "${:.1f}B",
        "Margin_Comp": "{:.1f}%",
        "XB_Exposure": "{:.1f}%",
        "Attractiveness_Score": "{:.1f}",
        "Est_Corpay_Addressable_Rev_M": "${:.1f}M"
    }), height=380)

# Strategic Recommendation Banner
top_segment = summary_df.iloc[0]["Segment"]
st.success(f"**Corp Dev Recommendation:** Based on your weights, Corpay should prioritize M&A or sales pipeline acquisition within the **{top_segment}** vertical to maximize automated payment cross-sell opportunities.")
