
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
# Cloud Cost Forecasting
st.subheader("Cloud Cost Forecasting")

total_cost = pd.to_numeric(
    results["monthly_cost"], errors="coerce"
).fillna(0).sum()

growth_rate = st.slider(
    "Expected monthly cost growth (%)",
    0, 30, 5,
    key="forecast_growth"
)

forecast_cost = total_cost * (1 + growth_rate / 100)

col1, col2 = st.columns(2)
col1.metric("Current Monthly Cost", f"₹{total_cost:,.0f}")
col2.metric("Estimated Next Month Cost", f"₹{forecast_cost:,.0f}")

forecast_data = pd.DataFrame({
    "Period": ["Current Month", "Next Month Forecast"],
    "Cost (₹)": [total_cost, forecast_cost]
})

fig_forecast = px.bar(
    forecast_data,
    x="Period",
    y="Cost (₹)",
    title="Monthly Cloud Cost Forecast"
)

st.plotly_chart(fig_forecast, width="stretch")

st.caption("This is an illustrative estimate, not a prediction from historical billing data.")

# What-If Savings Simulator
st.subheader("What-If Savings Simulator")

savings_percent = st.slider(
    "Potential cost reduction (%)",
    min_value=0,
    max_value=50,
    value=20,
    key="what_if_savings"
)

potential_savings = total_cost * savings_percent / 100
optimized_cost = total_cost - potential_savings

col1, col2, col3 = st.columns(3)
col1.metric("Current Cost", f"₹{total_cost:,.0f}")
col2.metric("Potential Savings", f"₹{potential_savings:,.0f}")
col3.metric("Cost After Optimization", f"₹{optimized_cost:,.0f}")

st.caption("Savings are illustrative estimates, not guaranteed real-world savings.")
