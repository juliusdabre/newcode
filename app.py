import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.preprocessing import MinMaxScaler
from fpdf import FPDF
import base64
import io

# Page setup
st.set_page_config("Smart Property Investment Dashboard", layout="wide")
st.title("📊 Smart Property Investment Dashboard")

# Load data
file_path = "Region Charts Master.xlsx"
price_df = pd.read_excel(file_path, sheet_name="House Price Sa3")
rent_df = pd.read_excel(file_path, sheet_name="House Rents")
seifa_df = pd.read_excel(file_path, sheet_name="Average SEIFA")
jobs_df = pd.read_excel(file_path, sheet_name="Jobs By Category")
suburbs_df = pd.read_excel(file_path, sheet_name="Suburbs Per SA3")

# Clean and prepare data
price_df = price_df.dropna(subset=["SA3"])
rent_df = rent_df.dropna(subset=["SA3"])
seifa_df = seifa_df.dropna(subset=["SA3"])
jobs_df = jobs_df.dropna(subset=["SA3"])

# Use the last 6 months for trends
price_cols = price_df.columns[-6:]
rent_cols = rent_df.columns[-6:]

# Merge data
merged = price_df[["SA3"] + list(price_cols)].merge(
    rent_df[["SA3"] + list(rent_cols)], on="SA3", suffixes=('_price', '_rent')
).merge(
    seifa_df[["SA3", "Average SEIFA"]], on="SA3"
).merge(
    jobs_df.groupby("SA3").sum().reset_index(), on="SA3"
)

# Compute scores
merged["price_growth"] = merged[price_cols].pct_change(axis=1).mean(axis=1)
merged["rent_growth"] = merged[rent_cols].pct_change(axis=1).mean(axis=1)
merged["job_diversity"] = jobs_df.drop(columns=["SA3"]).count(axis=1)

scaler = MinMaxScaler()
merged[["price_score", "rent_score", "seifa_score", "job_score"]] = scaler.fit_transform(
    merged[["price_growth", "rent_growth", "Average SEIFA", "job_diversity"]]
)

merged["total_score"] = merged[["price_score", "rent_score", "seifa_score", "job_score"]].sum(axis=1)

# Sidebar filters
sa3_options = merged.sort_values("total_score", ascending=False)["SA3"].unique()
seifa_min = int(merged["Average SEIFA"].min())
seifa_max = int(merged["Average SEIFA"].max())

selected_region = st.sidebar.selectbox("Select SA3 Region", sa3_options)
seifa_filter = st.sidebar.slider("Filter by SEIFA Score Range", seifa_min, seifa_max, (seifa_min, seifa_max))

# Apply SEIFA filter
merged_filtered = merged[(merged["Average SEIFA"] >= seifa_filter[0]) & (merged["Average SEIFA"] <= seifa_filter[1])]
selected_data = merged_filtered[merged_filtered["SA3"] == selected_region]

# Show charts
st.subheader(f"📈 Trends and Scores for {selected_region}")
col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Price Trend")
    fig_price = px.line(price_df[price_df["SA3"] == selected_region].T[2:], title="Price Trend")
    st.plotly_chart(fig_price, use_container_width=True)

with col2:
    st.markdown("#### Rent Trend")
    fig_rent = px.line(rent_df[rent_df["SA3"] == selected_region].T[2:], title="Rent Trend")
    st.plotly_chart(fig_rent, use_container_width=True)

# Map preview
st.subheader("📍 Map Preview (static)")
if 'Latitude' in suburbs_df.columns and 'Longitude' in suburbs_df.columns:
    loc = suburbs_df[suburbs_df['SA3'] == selected_region]
    fig_map = px.scatter_mapbox(loc, lat="Latitude", lon="Longitude", zoom=6)
    fig_map.update_layout(mapbox_style="carto-positron")
    st.plotly_chart(fig_map, use_container_width=True)
else:
    st.warning("Latitude and Longitude columns are missing in 'Suburbs Per SA3'. Map cannot be displayed.")

# Scores display
st.subheader("📊 Growth Scores")
st.dataframe(selected_data[["SA3", "price_score", "rent_score", "seifa_score", "job_score", "total_score"]].round(3))

# Top 20 Ranking
st.subheader("🏆 Top 20 SA3s Predicted to Grow")
st.dataframe(merged_filtered.sort_values("total_score", ascending=False)[["SA3", "total_score"]].head(20))

# Export PDF function
def generate_pdf(sa3, data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Growth Summary Report: {sa3}", ln=True, align='C')
    pdf.ln(10)
    for col in ["price_score", "rent_score", "seifa_score", "job_score", "total_score"]:
        score = data[col].values[0]
        pdf.cell(200, 10, txt=f"{col.replace('_', ' ').capitalize()}: {score:.3f}", ln=True)
    return pdf.output(dest='S').encode('latin1')

# Download button
if st.button("📄 Download SA3 Report as PDF"):
    pdf_bytes = generate_pdf(selected_region, selected_data)
    b64 = base64.b64encode(pdf_bytes).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="{selected_region}_report.pdf">Click here to download your PDF</a>'
    st.markdown(href, unsafe_allow_html=True)
