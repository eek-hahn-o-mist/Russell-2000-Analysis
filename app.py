import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import plotly.express as px

# Configuration
st.set_page_config(page_title="Corpay | Russell 2000 B2B Spend Modeler", layout="wide")

# 1. HARDCODED SYNTHESIZED DATASET
def get_historical_data():
    data = [
        {"Vertical": "Healthcare", "Year": 2023, "Spend_Billions": 120.5, "AI_MAUs_Millions": 1.2, "Core_Inflation": 4.1, "Margin_Compression_Pct": 2.1, "Cross_Border_Exposure_Pct": 12.0},
        {"Vertical": "Healthcare", "Year": 2024, "Spend_Billions": 128.2, "AI_MAUs_Millions": 1.8, "Core_Inflation": 3.4, "Margin_Compression_Pct": 2.3, "Cross_Border_Exposure_Pct": 12.5},
        {"Vertical": "Healthcare", "Year": 2025, "Spend_Billions": 136.8, "AI_MAUs_Millions": 2.5, "Core_Inflation": 2.8, "Margin_Compression_Pct": 2.5, "Cross_Border_Exposure_Pct": 13.1},
        
        {"Vertical": "Manufacturing", "Year": 2023, "Spend_Billions": 210.0, "AI_MAUs_Millions": 0.8, "Core_Inflation": 4.1, "Margin_Compression_Pct": 4.2, "Cross_Border_Exposure_Pct": 28.0},
        {"Vertical": "Manufacturing", "Year": 2024, "Spend_Billions": 222.5, "AI_MAUs_Millions": 1.1, "Core_Inflation": 3.4, "Margin_Compression_Pct": 4.5, "Cross_Border_Exposure_Pct": 29.5},
        {"Vertical": "Manufacturing", "Year": 2025, "Spend_Billions": 238.1, "AI_MAUs_Millions": 1.5, "Core_Inflation": 2.8, "Margin_Compression_Pct": 4.9, "Cross_Border_Exposure_Pct": 31.0},
        
        {"Vertical": "Professional Services", "Year": 2023, "Spend_Billions": 85.2, "AI_MAUs_Millions": 3.5, "Core_Inflation": 4.1, "Margin_Compression_Pct": 1.1, "Cross_Border_Exposure_Pct": 18.0},
        {"Vertical": "Professional Services", "Year": 2024, "Spend_Billions": 94.8, "AI_MAUs_Millions": 5.2, "Core_Inflation": 3.4, "Margin_Compression_Pct": 1.2, "Cross_Border_Exposure_Pct": 20.5},
        {"Vertical": "Professional Services", "Year": 2025, "Spend_Billions": 105.4, "AI_MAUs_Millions": 7.8, "Core_Inflation": 2.8, "Margin_Compression_Pct": 1.4, "Cross_Border_Exposure_Pct": 22.0},
        
        {"Vertical": "Logistics/Wholesale", "Year": 2023, "Spend_Billions": 185.0, "AI_MAUs_Millions": 0.5, "Core_Inflation": 4.1, "Margin_Compression_Pct": 3.1, "Cross_Border_Exposure_Pct": 42.0},
        {"Vertical": "Logistics/Wholesale", "Year": 2024, "Spend_Billions": 201.3, "AI_MAUs_Millions": 0.9, "Core_Inflation": 3.4, "Margin_Compression_Pct": 3.5, "Cross_Border_Exposure_Pct": 44.5},
        {"Vertical": "Logistics/Wholesale", "Year": 2025, "Spend_Billions": 218.9, "AI_MAUs_Millions": 1.4, "Core_Inflation": 2.8, "Margin_Compression_Pct": 3.9, "Cross_Border_Exposure_Pct": 47.0},
        
        {"Vertical": "Construction", "Year": 2023, "Spend_Billions": 98.4, "AI_MAUs_Millions": 0.2, "Core_Inflation": 4.1, "Margin_Compression_Pct": 5.2, "Cross_Border_Exposure_Pct": 4.5},
        {"Vertical": "Construction", "Year": 2024, "Spend_Billions": 106.1, "AI_MAUs_Millions": 0.4, "Core_Inflation": 3.4, "Margin_Compression_Pct": 5.8, "Core_Inflation": 3.4, "Margin_Compression_Pct": 5.8, "Cross_Border_Exposure_Pct": 5.1},
        {"Vertical": "Construction", "Year": 2025, "Spend_Billions": 114.7, "AI_MAUs_Millions": 0.7, "Core_Inflation": 2.8, "Margin_Compression_Pct": 6.3, "Cross_Border_Exposure_Pct": 5.8},
    ]
    return pd.DataFrame(data)

# 2. FORECASTING & REGRESSION
def forecast_spend(df):
    verticals = df['Vertical'].unique()
    forecast_results = []
    coefficients = {}
    
    for v in verticals:
        subset = df[df['Vertical'] == v]
        X = subset[['Year']].values
        y = subset['Spend_Billions'].values
        
        model = LinearRegression()
        model.fit(X, y)
        coefficients[v] = model.coef_[0]
        
        # Predict 2026, 2027
        years_to_predict = np.array([[2026], [2027]])
        predictions = model.predict(years_to_predict)
        
        # Latest values for other variables (holding steady/trending for score calculation)
        last_row = subset.iloc[-1]
        
        for i, year in enumerate([2026, 2027]):
            forecast_results.append({
                "Vertical": v,
                "Year": year,
                "Spend_Billions": predictions[i],
                "AI_MAUs_Millions": last_row['AI_MAUs_Millions'] * (1.2 ** (i+1)), # Synthetic growth
                "Core_Inflation": 2.5, # Assume target inflation
                "Margin_Compression_Pct": last_row['Margin_Compression_Pct'],
                "Cross_Border_Exposure_Pct": last_row['Cross_Border_Exposure_Pct'],
                "Type": "Forecast"
            })
            
    df['Type'] = 'Historical'
    forecast_df = pd.DataFrame(forecast_results)
    return pd.concat([df, forecast_df], ignore_index=True), coefficients

# Sidebar UI
st.sidebar.title("Corpay Strategy Weights")
w_spend = st.sidebar.slider("Weight: Total Spend Volume", 0.0, 1.0, 0.4)
w_cross = st.sidebar.slider("Weight: Cross-Border Exposure", 0.0, 1.0, 0.4)
w_margin = st.sidebar.slider("Weight: Margin Compression", 0.0, 1.0, 0.2)

# Calculations
raw_df = get_historical_data()
full_df, regression_coefs = forecast_spend(raw_df)

# Attractiveness Matrix Calculation (Based on 2025 Data)
latest_data = full_df[full_df['Year'] == 2025].copy()
norm_spend = (latest_data['Spend_Billions'] - latest_data['Spend_Billions'].min()) / (latest_data['Spend_Billions'].max() - latest_data['Spend_Billions'].min())
norm_cross = (latest_data['Cross_Border_Exposure_Pct'] - latest_data['Cross_Border_Exposure_Pct'].min()) / (latest_data['Cross_Border_Exposure_Pct'].max() - latest_data['Cross_Border_Exposure_Pct'].min())
norm_margin = (latest_data['Margin_Compression_Pct'] - latest_data['Margin_Compression_Pct'].min()) / (latest_data['Margin_Compression_Pct'].max() - latest_data['Margin_Compression_Pct'].min())

latest_data['Attractiveness_Score'] = (norm_spend * w_spend) + (norm_cross * w_cross) + (norm_margin * w_margin)
latest_data['Addressable_Net_Revenue_M'] = (latest_data['Spend_Billions'] * 1000) * 0.0062

# Recommendation Engine
recommendations = latest_data.sort_values(by='Attractiveness_Score', ascending=False).head(3)

# Main Dashboard UI
st.title("Russell 2000 B2B Spend Forecast & M&A Analysis")
st.markdown("### Strategic Market Segmentation for Corpay Corporate Development")

col1, col2 = st.columns([2, 1])

with col1:
    fig = px.bar(
        full_df, 
        x='Year', 
        y='Spend_Billions', 
        color='Vertical', 
        barmode='group',
        title="Historical (2023-25) vs Projected (2026-27) Non-Salary Spend ($B)",
        labels={'Spend_Billions': 'Spend ($ Billions)'},
        color_discrete_sequence=px.colors.qualitative.Prism,
        pattern_shape="Type",
        pattern_shape_sequence=["", ""]
    )
    fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Top M&A Targets")
    for i, row in recommendations.iterrows():
        st.metric(f"{row['Vertical']}", f"Score: {row['Attractiveness_Score']:.2f}", f"${row['Addressable_Net_Revenue_M']:.1f}M Net Rev")

# Data Table Matrix
st.subheader("Market Segment Analysis Matrix")
matrix_display = latest_data[[
    'Vertical', 'Spend_Billions', 'Cross_Border_Exposure_Pct', 
    'Margin_Compression_Pct', 'Attractiveness_Score', 'Addressable_Net_Revenue_M'
]].copy()

# Add regression coefficients
matrix_display['Growth_Slope_Coef'] = matrix_display['Vertical'].map(regression_coefs)

st.dataframe(
    matrix_display.style.background_gradient(subset=['Attractiveness_Score'], cmap='Greens')
    .format({'Spend_Billions': '${:,.1f}B', 'Addressable_Net_Revenue_M': '${:,.1f}M', 'Attractiveness_Score': '{:.2f}'}),
    use_container_width=True
)

st.info("**Methodology:** Net Revenue assumes Corpay's 62bps take rate on total addressable volume. Margin compression serves as a proxy for 'Pain Point Intensity,' driving AP Automation (Paymerang/Corpay Complete) adoption.")
