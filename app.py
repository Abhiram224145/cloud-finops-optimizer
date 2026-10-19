
import streamlit as st
import pandas as pd
import plotly.express as px

from analyzer import analyze_resources

st.set_page_config(
    page_title="Cloud FinOps Optimizer",
    page_icon="☁️",
    layout="wide"
)

st.title("☁️ Intelligent Cloud FinOps Optimization Engine")
st.write("Detect cloud resource waste and estimate potential savings.")

uploaded_file = st.file_uploader(
    "Upload your cloud resources CSV file",
    type=["csv"]
)

try:
    if uploaded_file is not None:
        raw_data = pd.read_csv(uploaded_file)
    else:
        raw_data = pd.read_csv("cloud_resources.csv")

    results = analyze_resources(raw_data)

except Exception as error:
    st.error(f"Unable to analyze data: {error}")
    st.stop()

total_cost = results["monthly_cost"].sum()
total_savings = results["estimated_savings"].sum()

flagged = (
    results["recommendation"] != "Normal usage"
).sum()

anomalies = results["anomaly"].sum()

col1, col2, col3, col4 = st.columns(4)

col1.metric("Monthly Cloud Cost", f"₹{total_cost:,.0f}")
col2.metric("Estimated Savings", f"₹{total_savings:,.0f}")
col3.metric("Resources to Review", int(flagged))
col4.metric("ML Anomalies", int(anomalies))

st.subheader("Monthly Cost by Resource")

fig = px.bar(
    results,
    x="resource_id",
    y="monthly_cost",
    color="recommendation",
    title="Cloud Resource Cost Analysis",
    labels={
        "resource_id": "Resource",
        "monthly_cost": "Monthly Cost (₹)",
        "recommendation": "Recommendation"
    }
)

st.plotly_chart(fig, use_container_width=True)

st.subheader("AI/ML Analysis Results")

st.dataframe(
    results,
    use_container_width=True,
    hide_index=True
)

report = results.to_csv(index=False).encode("utf-8")

st.download_button(
    "Download Analysis Report",
    data=report,
    file_name="cloud_finops_report.csv",
    mime="text/csv"
)
