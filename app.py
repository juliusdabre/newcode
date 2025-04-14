import zipfile
import os

# Define file paths
app_file_path = "/mnt/data/app.py"
csv_file_path = "/mnt/data/sa3_clean.csv"
excel_file_path = "/mnt/data/Suburb Excel and Radar January 2025.xlsx"
zip_path = "/mnt/data/smart_property_app_bundle.zip"

# Write the app content to app.py
app_code = '''import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Load cleaned SA3 and Suburb data
sa3_df = pd.read_csv("sa3_clean.csv")
suburb_df = pd.read_excel("Suburb Excel and Radar January 2025.xlsx", sheet_name="Suburb", header=6)
suburb_df = suburb_df.dropna(axis=1, how='all')
suburb_df = suburb_df.dropna(subset=[suburb_df.columns[0]])
suburb_df = suburb_df.reset_index(drop=True)

st.set_page_config("Smart Property Investment Tool", layout="wide")
st.title("🏠 Smart Property Investment Tool")

# Sidebar filters
with st.sidebar:
    st.header("Filter by SA3 Metrics")
    growth_gap = st.slider("Growth Gap", 1, 5, (1, 5))
    price_change = st.slider("12M Price Change", 1, 5, (1, 5))
    yield_range = st.slider("Rental Yield %", 0.0, 10.0, (3.0, 7.0))
    afford_buy = st.slider("Buy Affordability (Score)", 1, 5, (1, 5))
    afford_rent = st.slider("Rent Affordability (Score)", 0.0, 1.0, (0.2, 0.6))

# Apply filters
filtered_df = sa3_df[
    (sa3_df['Growth Gap'].between(*growth_gap)) &
    (sa3_df['12M Price Change'].between(*price_change)) &
    (sa3_df['YIELD'].between(*yield_range)) &
    (sa3_df['Buy Affordability'].between(*afford_buy)) &
    (sa3_df['Rent Afford'].between(*afford_rent))
]

st.subheader("Filtered SA3 Regions")
st.dataframe(filtered_df[['SA3', 'Median', 'Growth Gap', '12M Price Change', 'YIELD', 'Radar Index']].sort_values(by='Radar Index', ascending=False))

# Radar chart comparison
st.subheader("📊 SA3 Radar Chart Comparison")
selected_sa3s = st.multiselect("Select SA3s to Compare", options=filtered_df['SA3'].unique())

if selected_sa3s:
    radar_data = filtered_df[filtered_df['SA3'].isin(selected_sa3s)]
    categories = ['Growth Gap', '12M Price Change', 'YIELD', 'Buy Affordability', 'Rent Afford']

    fig = go.Figure()
    for _, row in radar_data.iterrows():
        fig.add_trace(go.Scatterpolar(
            r=[row[cat] for cat in categories],
            theta=categories,
            fill='toself',
            name=row['SA3']
        ))

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
        showlegend=True
    )
    st.plotly_chart(fig, use_container_width=True)

# Suburb insights
st.subheader("🏘️ Suburb Investment Insights")
selected_suburb = st.selectbox("Select a Suburb", suburb_df['Location'].unique())

if selected_suburb:
    sub_data = suburb_df[suburb_df['Location'] == selected_suburb].iloc[0]
    st.markdown(f"**Nearest SA2:** {sub_data['Unnamed: 4']}")
    st.markdown(f"**SA3:** {sub_data['Unnamed: 5']} | **Region:** {sub_data['Unnamed: 6']}")
    st.markdown(f"**Property Type:** {sub_data['Suburb Metrics Estimates']}")

    st.metric("Investor Score", int(sub_data['Investor Score (Out Of 100)']))
    st.metric("Growth Gap Index", int(sub_data['Growth Gap Index']))
    st.metric("Yield Score", int(sub_data['Yield Score']))
    st.metric("Buy Affordability", int(sub_data['Buy Affordability Score']))
    st.metric("Rent Affordability", int(sub_data['Rent Affordability Score']))

st.markdown("---")
st.caption("Built with ❤️ by Propwealth")
'''

with open(app_file_path, "w") as f:
    f.write(app_code)

# Create a ZIP bundle
with zipfile.ZipFile(zip_path, "w") as bundle:
    bundle.write(app_file_path, arcname="app.py")
    bundle.write(csv_file_path, arcname="sa3_clean.csv")
    bundle.write(excel_file_path, arcname="Suburb Excel and Radar January 2025.xlsx")

zip_path
