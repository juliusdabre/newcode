import zipfile
import os

# Save the manually pasted code
code = '''import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

# Load data
file_path = "Region Charts Master.xlsx"
price_df = pd.read_excel(file_path, sheet_name="House Price Sa3")
rent_df = pd.read_excel(file_path, sheet_name="House Rents")
vacancy_df = pd.read_excel(file_path, sheet_name="Vacancy Rates")
inventory_df = pd.read_excel(file_path, sheet_name="House Inventory Sa3")
seifa_df = pd.read_excel(file_path, sheet_name="Average SEIFA")
ai_df = pd.read_excel(file_path, sheet_name="AI Impact")
jobs_df = pd.read_excel(file_path, sheet_name="Jobs By Category")
suburbs_df = pd.read_excel(file_path, sheet_name="Suburbs Per SA3")

# Page setup
st.set_page_config("Smart Property Investment Dashboard", layout="wide")
st.title("🏠 Smart Property Investment Dashboard")

# Sidebar filter
regions = sorted(price_df['SA3'].dropna().unique())
selected_region = st.sidebar.selectbox("Select SA3 Region", regions)

# Filtered data
price_filtered = price_df[price_df['SA3'] == selected_region]
rent_filtered = rent_df[rent_df['SA3'] == selected_region]
vacancy_filtered = vacancy_df[vacancy_df['SA3'] == selected_region]
inventory_filtered = inventory_df[inventory_df['SA3'] == selected_region]
seifa_score = seifa_df[seifa_df['Row Labels'] == selected_region]
ai_score = ai_df[ai_df['Row Labels'] == selected_region]
jobs_filtered = jobs_df[jobs_df['Row Labels'] == selected_region]

# Tabs for organized view
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Price Trends", "Rent Trends", "Vacancy + Inventory", "SEIFA + AI", "Score & Map"])

with tab1:
    st.subheader("📈 Median House Price")
    melt_price = price_filtered.melt(id_vars='SA3', var_name='Month', value_name='Price')
    fig_price = px.line(melt_price, x='Month', y='Price', title="House Price Trend")
    st.plotly_chart(fig_price, use_container_width=True)

with tab2:
    st.subheader("💰 Median Weekly Rent")
    melt_rent = rent_filtered.melt(id_vars='SA3', var_name='Month', value_name='Rent')
    fig_rent = px.line(melt_rent, x='Month', y='Rent', title="House Rent Trend")
    st.plotly_chart(fig_rent, use_container_width=True)

with tab3:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📉 Vacancy Rates")
        melt_vac = vacancy_filtered.melt(id_vars='SA3', var_name='Month', value_name='Vacancy Rate')
        fig_vac = px.line(melt_vac, x='Month', y='Vacancy Rate')
        st.plotly_chart(fig_vac, use_container_width=True)
    with col2:
        st.subheader("🏘 Inventory Levels")
        melt_inv = inventory_filtered.melt(id_vars='SA3', var_name='Month', value_name='Inventory')
        fig_inv = px.line(melt_inv, x='Month', y='Inventory')
        st.plotly_chart(fig_inv, use_container_width=True)

with tab4:
    st.subheader("🔍 Socioeconomic Indicators")
    st.metric("SEIFA Score", seifa_score['Average of Advantage Disadvantage Decile'].values[0] if not seifa_score.empty else "N/A")
    st.metric("AI Impact", ai_score['Sum of Total People Potentially  Impacted'].values[0] if not ai_score.empty else "N/A")
    st.dataframe(jobs_filtered[['MAX', 'Concentration Risk']], use_container_width=True)

with tab5:
    st.subheader("📊 Composite Investment Score (Demo)")
    try:
        score = (
            seifa_score['Average of Advantage Disadvantage Decile'].values[0] +
            ai_score['Sum of Total People Potentially  Impacted'].values[0] +
            jobs_filtered['Concentration Risk'].values[0]
        ) / 3
        st.success(f"Composite Score for {selected_region}: {round(score, 2)}")
    except:
        st.warning("Score data not available for this region.")

    st.subheader("📍 Map Preview (static)")
    loc = suburbs_df[suburbs_df['SA3'] == selected_region]
    if not loc.empty:
        fig_map = px.scatter_mapbox(loc, lat="Latitude", lon="Longitude", zoom=6, height=400)
        fig_map.update_layout(mapbox_style="carto-positron")
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.info("No map location data available.")
'''

# Write to file
os.makedirs("/mnt/data/smart_property_investment_bundle", exist_ok=True)
with open("/mnt/data/smart_property_investment_bundle/app.py", "w") as f:
    f.write(code)

# Generate ZIP (without Excel, user needs to add it manually after download)
zip_path = "/mnt/data/SmartPropertyInvestmentApp.zip"
with zipfile.ZipFile(zip_path, "w") as zipf:
    zipf.write("/mnt/data/smart_property_investment_bundle/app.py", arcname="app.py")

zip_path
