import streamlit as st
import plotly.express as px

# Extract the columns for the latest months (assume last 6 for rental and price trends)
price_trend_cols = price_df.columns[-8:]
rent_trend_cols = rent_df.columns[-8:]

# Drop rows with missing SA3
price_df = price_df.dropna(subset=["SA3"])
rent_df = rent_df.dropna(subset=["SA3"])
seifa_df = seifa_df.dropna(subset=["SA3"])
jobs_df = jobs_df.dropna(subset=["SA3"])

# Merge all into a single DataFrame for unified access
merged_df = price_df[["SA3"] + list(price_trend_cols)].merge(
    rent_df[["SA3"] + list(rent_trend_cols)], on="SA3", suffixes=("_price", "_rent")
).merge(
    seifa_df[["SA3", "Average SEIFA"]], on="SA3"
).merge(
    jobs_df.groupby("SA3").sum().reset_index(), on="SA3"
)

# Normalize columns to compute growth scores
from sklearn.preprocessing import MinMaxScaler

trend_cols = list(price_trend_cols) + list(rent_trend_cols)
score_data = merged_df.copy()
score_data["price_growth"] = score_data[price_trend_cols].pct_change(axis=1).mean(axis=1)
score_data["rent_growth"] = score_data[rent_trend_cols].pct_change(axis=1).mean(axis=1)
score_data["seifa_score"] = score_data["Average SEIFA"]
score_data["job_diversity"] = jobs_df.drop(columns=["SA3"]).apply(lambda x: x.count(), axis=1)

scaler = MinMaxScaler()
score_data[["price_score", "rent_score", "seifa_score_scaled", "job_score"]] = scaler.fit_transform(
    score_data[["price_growth", "rent_growth", "seifa_score", "job_diversity"]]
)

# Total Score: Higher is better
score_data["total_score"] = (
    score_data["price_score"] +
    score_data["rent_score"] +
    score_data["seifa_score_scaled"] +
    score_data["job_score"]
)

# Sort SA3s based on total score
top_sa3s = score_data.sort_values("total_score", ascending=False)[["SA3", "total_score"]]

tools.display_dataframe_to_user(name="Top SA3s Predicted to Grow", dataframe=top_sa3s.head(20))
