import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.linear_model import LinearRegression

# Page configuration
st.set_page_config(page_title="Corpay Corp Dev Analytics", layout="wide")

st.title("Corpay Corporate Development Hub")

# Establish the multi-tab layout architecture
tab1, tab2 = st.tabs(["📊 Russell 2000 Spend Forecast", "🇲🇽 Mexico Vehicle Wallet Blueprint"])

# ==============================================================================
# TAB 1: RUSSELL 2000 SPEND FORECAST
# ==============================================================================
with tab1:
    st.subheader("Part 1: Russell 2000 B2B Spend Forecast & Segment Selection Matrix")

    # --- 1. HARDCODED SYNTHESIZED DATASET ---
    @st.cache_data
    def load_russell_data():
        segments = ["Healthcare", "Manufacturing", "Professional Services", "Logistics/Wholesale", "Construction"]
        years = [2023, 2024, 2025]
        
        data_list = []
        raw_history = {
            "Healthcare": {"spend": [45.2, 48.5, 52.1], "margin_comp": 3.4, "xb_exposure": 12.0},
            "Manufacturing": {"spend": [68.0, 71.2, 73.8], "margin_comp": 4.1, "xb_exposure": 28.0},
            "Professional Services": {"spend": [32.1, 35.8, 39.5], "margin_comp": 1.8, "xb_exposure": 18.0},
            "Logistics/Wholesale": {"spend": [55.0, 59.4, 64.2], "margin_comp": 5.2, "xb_exposure": 35.0},
            "Construction": {"spend": [40.5, 42.1, 43.8], "margin_comp": 2.5, "xb_exposure": 8.0}
        }
        
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

    df_russell = load_russell_data()

    # --- 2. FORECASTING & LINEAR REGRESSION LOGIC ---
    forecasted_data = []
    segments = df_russell["Segment"].unique()

    for seg in segments:
        seg_df = df_russell[df_russell["Segment"] == seg]
        X = seg_df[["Year"]].values
        y = seg_df["Non_Salary_Spend_B"].values
        
        model = LinearRegression()
        model.fit(X, y)
        
        future_years = np.array([[2026], [2027]])
        predictions = model.predict(future_years)
        
        for _, row in seg_df.iterrows():
            forecasted_data.append({
                "Segment": seg, "Year": int(row["Year"]), "Spend_B": row["Non_Salary_Spend_B"],
                "Type": "Historical", "Margin_Comp": row["Margin_Compression"], "XB_Exposure": row["Cross_Border_Exposure"]
            })
        for idx, yr in enumerate([2026, 2027]):
            forecasted_data.append({
                "Segment": seg, "Year": yr, "Spend_B": predictions[idx],
                "Type": "Projected", "Margin_Comp": seg_df["Margin_Compression"].iloc[0], "XB_Exposure": seg_df["Cross_Border_Exposure"].iloc[0]
            })

    df_all = pd.DataFrame(forecasted_data)

    # --- 3. SIDEBAR CONTROLS ---
    st.sidebar.header("M&A Strategy Parameters")
    st.sidebar.subheader("Russell 2000 Weights")
    w_volume = st.sidebar.slider("Spend Volume Weight", 0.0, 1.0, 0.4, 0.1)
    w_margin = st.sidebar.slider("Margin Compression Weight", 0.0, 1.0, 0.3, 0.1)
    w_xb = st.sidebar.slider("Cross-Border Exposure Weight", 0.0, 1.0, 0.3, 0.1)

    st.sidebar.markdown("---")
    st.sidebar.subheader("Corpay Unit Economics")
    take_rate = st.sidebar.number_input("Net Take Rate (%)", value=0.62, step=0.01) / 100

    # --- 4. DISPLAY CHARTS & TABLES ---
    st.write("### Historical vs. Projected Spend Volumes ($ Billions)")
    fig_bar = px.bar(df_all, x="Year", y="Spend_B", color="Segment", barmode="group",
                 labels={"Spend_B": "Non-Salary Spend ($B)", "Year": "Fiscal Year"},
                 color_discrete_sequence=px.colors.qualitative.Plotly)
    st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("---")
    st.write("### Strategic Priorities (2027 View)")

    df_2027 = df_all[df_all["Year"] == 2027].copy()

    def normalize(col):
        return (col - col.min()) / (col.max() - col.min()) if (col.max() - col.min()) != 0 else 1.0

    df_2027["Norm_Volume"] = normalize(df_2027["Spend_B"])
    df_2027["Norm_Margin"] = normalize(df_2027["Margin_Comp"])
    df_2027["Norm_XB"] = normalize(df_2027["XB_Exposure"])

    df_2027["Attractiveness_Score"] = (
        (df_2027["Norm_Volume"] * w_volume) +
        (df_2027["Norm_Margin"] * w_margin) +
        (df_2027["Norm_XB"] * w_xb)
    ) * 100

    df_2027["Est_Corpay_Addressable_Rev_M"] = (df_2027["Spend_B"] * take_rate) * 1000
    summary_df = df_2027[["Segment", "Spend_B", "Margin_Comp", "XB_Exposure", "Attractiveness_Score", "Est_Corpay_Addressable_Rev_M"]].sort_values(by="Attractiveness_Score", ascending=False)

    st.dataframe(summary_df.style.format({
        "Spend_B": "${:.1f}B",
        "Margin_Comp": "{:.1f}%",
        "XB_Exposure": "{:.1f}%",
        "Attractiveness_Score": "{:.1f}",
        "Est_Corpay_Addressable_Rev_M": "${:.1f}M"
    }), use_container_width=True)

    top_segment = summary_df.iloc[0]["Segment"]
    st.success(f"**Corp Dev Recommendation:** Prioritize M&A or sales pipeline acquisition within the **{top_segment}** vertical to maximize automated payment cross-sell opportunities.")


# ==============================================================================
# TAB 2: MEXICO VEHICLE SOLUTIONS BLUEPRINT
# ==============================================================================
with tab2:
    st.subheader("Part 2: Mexico Geographic Fleet Expansion & Compliance Monetization Map")
    st.write(
        "Replicating the Brazilian 'Vehicle Wallet' framework (Zapay/Gringo) requires identifying regions with a strong mix of physical transaction points "
        "and high compliance friction (local traffic fines and registration complexities)."
    )

    # --- 1. HARDCODED MEXICO REGIONAL DATASET ---
    @st.cache_data
    def load_mexico_data():
        mexico_regions = {
            # Standardized strings matching the upcoming GeoJSON boundary descriptors
            "State/Region": ["Distrito Federal", "México", "Nuevo León", "Jalisco"],
            "Display_Name": ["CDMX (Valle de México)", "Estado de México", "Nuevo León", "Jalisco"],
            "Registered_Vehicles_M": [5.6, 8.1, 2.7, 4.1],
            "Toll_Plazas_Count": [12, 28, 14, 22],
            "Fast_Food_QSR_Locations": [450, 620, 290, 340],
            "Annual_Fine_Volume_M": [3.1, 4.8, 1.2, 1.9],
            "Fine_Complexity_Score": [9.5, 8.5, 6.0, 7.5],  
            "Smartphone_Penetration_Pct": [88.5, 79.2, 86.0, 82.4]
        }
        return pd.DataFrame(mexico_regions)

    df_mexico = load_mexico_data()

    # --- 2. CONTEXTUAL SIDEBAR CONTROLS ---
    st.sidebar.subheader("Mexico Digital Wallet Weights")
    w_fines = st.sidebar.slider("Fine Complexity
