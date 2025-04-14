import streamlit as st
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

# Sidebar filters
st.sidebar.header("🔍 Filter Options")
regions = sorted(price_df['SA3'].dropna().unique())
selected_region = st.sidebar.selectbox("Select SA3 Region", regions)

time_columns = [col for col in price_df.columns if col not in ['SA3', 'SA4']]
selected_months = st.sidebar.multiselect("Select Months to Compare", time_columns, default=time_columns[-6:])

metric_options = ['Price', 'Rent', 'Vacancy', 'Inventory', 'SEIFA Score', 'AI Impact', 'Job Risk']
selected_metrics = st.sidebar.multiselect("Select Metrics to Display", metric_options, default=metric_options)

# Additional filters
st.sidebar.markdown("---")
track_price_rise = st.sidebar.checkbox("🔼 Track Suburbs with Rising Prices")
track_rent_rise = st.sidebar.checkbox("🔼 Track Suburbs with Rising Rents")

# Filtered data
# Apply price/rent rise logic to show alerts across all SA3s
if track_price_rise:
    rising_price_sa3s = []
    for sa3 in regions:
        series = price_df[price_df['SA3'] == sa3][time_columns[-12:]].values.flatten()
        if len(series) >= 2 and series[-1] > series[0]:
            rising_price_sa3s.append(sa3)
    if selected_region in rising_price_sa3s:
        st.sidebar.success(f"📈 {selected_region} is experiencing a price rise over the last 12 months")
    else:
        st.sidebar.info(f"{selected_region} has no price rise in the last 12 months")

if track_rent_rise:
    rising_rent_sa3s = []
    for sa3 in regions:
        series = rent_df[rent_df['SA3'] == sa3][time_columns[-12:]].values.flatten()
        if len(series) >= 2 and series[-1] > series[0]:
            rising_rent_sa3s.append(sa3)
    if selected_region in rising_rent_sa3s:
        st.sidebar.success(f"📈 {selected_region} is experiencing a rent rise over the last 12 months")
    else:
        st.sidebar.info(f"{selected_region} has no rent rise in the last 12 months")
price_filtered = price_df[price_df['SA3'] == selected_region]
rent_filtered = rent_df[rent_df['SA3'] == selected_region]
vacancy_filtered = vacancy_df[vacancy_df['SA3'] == selected_region]
inventory_filtered = inventory_df[inventory_df['SA3'] == selected_region]
seifa_score = seifa_df[seifa_df['Row Labels'] == selected_region]
ai_score = ai_df[ai_df['Row Labels'] == selected_region]
jobs_filtered = jobs_df[jobs_df['Row Labels'] == selected_region]

# Tabs for organized view
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Price Trends", "Rent Trends", "Vacancy + Inventory", "SEIFA + AI", "Score & Map", "Job Risk"])

with tab1:
    if 'Price' in selected_metrics:
        st.subheader("📈 Median House Price")
        melt_price = price_filtered.melt(id_vars='SA3', value_vars=selected_months, var_name='Month', value_name='Price')
        fig_price = px.line(melt_price, x='Month', y='Price', title="House Price Trend")
        st.plotly_chart(fig_price, use_container_width=True)

with tab2:
    if 'Rent' in selected_metrics:
        st.subheader("💰 Median Weekly Rent")
        melt_rent = rent_filtered.melt(id_vars='SA3', value_vars=selected_months, var_name='Month', value_name='Rent')
        fig_rent = px.line(melt_rent, x='Month', y='Rent', title="House Rent Trend")
        st.plotly_chart(fig_rent, use_container_width=True)

with tab3:
    col1, col2 = st.columns(2)
    with col1:
        if 'Vacancy' in selected_metrics:
            st.subheader("📉 Vacancy Rates")
            melt_vac = vacancy_filtered.melt(id_vars='SA3', value_vars=selected_months, var_name='Month', value_name='Vacancy Rate')
            fig_vac = px.line(melt_vac, x='Month', y='Vacancy Rate')
            st.plotly_chart(fig_vac, use_container_width=True)
    with col2:
        if 'Inventory' in selected_metrics:
            st.subheader("🏘 Inventory Levels")
            melt_inv = inventory_filtered.melt(id_vars='SA3', value_vars=selected_months, var_name='Month', value_name='Inventory')
            fig_inv = px.line(melt_inv, x='Month', y='Inventory')
            st.plotly_chart(fig_inv, use_container_width=True)

with tab4:
    st.subheader("🔍 Socioeconomic Indicators")
    if 'SEIFA Score' in selected_metrics:
        st.metric("SEIFA Score", seifa_score['Average of Advantage Disadvantage Decile'].values[0] if not seifa_score.empty else "N/A")
    if 'AI Impact' in selected_metrics:
        st.metric("AI Impact", ai_score['Sum of Total People Potentially  Impacted'].values[0] if not ai_score.empty else "N/A")
    if 'Job Risk' in selected_metrics:
        st.metric("Job Risk Score", jobs_filtered['Concentration Risk'].values[0] if not jobs_filtered.empty else "N/A")
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
    if "Latitude" in loc.columns and "Longitude" in loc.columns:
        fig_map = px.scatter_mapbox(loc, lat="Latitude", lon="Longitude", zoom=6, height=400)
        fig_map.update_layout(mapbox_style="carto-positron")
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.info("Latitude and Longitude data not available for this SA3.")

with tab6:
    st.subheader("💼 Job Risk Breakdown")
    if not jobs_filtered.empty:
        st.dataframe(jobs_filtered, use_container_width=True)
        st.bar_chart(jobs_filtered.set_index('MAX')['Concentration Risk'])
    else:
        st.warning("No job risk data available for this region.")
