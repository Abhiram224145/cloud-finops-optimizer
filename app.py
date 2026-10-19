
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

st.plotly_chart(fig, width="stretch")

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

# -------------------------------
# Cloud Cost Forecasting
# -------------------------------

st.subheader("Cloud Cost Forecasting")

if "monthly_cost" in results.columns:
    total_cost = pd.to_numeric(
        results["monthly_cost"], errors="coerce"
    ).fillna(0).sum()

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Current Monthly Cost", f"₹{total_cost:,.0f}")

    with col2:
        growth_rate = st.slider(
            "Expected monthly cost growth (%)",
            min_value=0,
            max_value=30,
            value=5
        )

    forecast_cost = total_cost * (1 + growth_rate / 100)

    st.metric(
        "Estimated Next Month Cost",
        f"₹{forecast_cost:,.0f}",
        delta=f"₹{forecast_cost - total_cost:,.0f}"
    )

    forecast_data = pd.DataFrame({
        "Period": ["Current Month", "Next Month Forecast"],
        "Cost (₹)": [total_cost, forecast_cost]
    })

    fig_forecast = px.bar(
        forecast_data,
        x="Period",
        y="Cost (₹)",
        title="Monthly Cloud Cost Forecast",
        text_auto=".2s"
    )

    st.plotly_chart(fig_forecast, use_container_width=True)

    st.caption(
        "Forecast is a simple estimate based on your selected growth rate, "
        "not a prediction from historical billing data."
    )
else:
    st.warning(
        "The monthly_cost column was not found in the analysis results."
    )


# -------------------------------
# What-If Savings Simulator
# -------------------------------

st.subheader("What-If Savings Simulator")

if "monthly_cost" in results.columns:
    total_cost = pd.to_numeric(
        results["monthly_cost"], errors="coerce"
    ).fillna(0).sum()

    savings_percent = st.slider(
        "Potential cost reduction (%)",
        min_value=0,
        max_value=50,
        value=20,
        key="what_if_savings_percent"
    )

    potential_savings = total_cost * savings_percent / 100
    optimized_cost = total_cost - potential_savings

    col1, col2, col3 = st.columns(3)

    col1.metric("Current Cost", f"₹{total_cost:,.0f}")
    col2.metric("Potential Savings", f"₹{potential_savings:,.0f}")
    col3.metric("Cost After Optimization", f"₹{optimized_cost:,.0f}")

    st.caption(
        "Illustrative estimate only. Actual savings depend on "
        "resource usage and cloud pricing."
    )

# -------------------------------
# Resource Health Monitor
# -------------------------------

st.subheader("Resource Health Monitor")

health_data = results.copy()

required_columns = [
    "resource_id", "cpu_usage", "memory_usage"
]

if all(col in health_data.columns for col in required_columns):
    health_data["cpu_usage"] = pd.to_numeric(
        health_data["cpu_usage"], errors="coerce"
    )
    health_data["memory_usage"] = pd.to_numeric(
        health_data["memory_usage"], errors="coerce"
    )

    health_data = health_data.dropna(
        subset=["cpu_usage", "memory_usage"]
    )

    def get_health(row):
        if row["cpu_usage"] < 10 and row["memory_usage"] < 20:
            return "Underutilized"
        elif row["cpu_usage"] > 90 or row["memory_usage"] > 90:
            return "Needs Review"
        return "Healthy"

    health_data["health_status"] = health_data.apply(
        get_health, axis=1
    )

    st.dataframe(
        health_data[
            [
                "resource_id",
                "cpu_usage",
                "memory_usage",
                "health_status"
            ]
        ],
        use_container_width=True,
        hide_index=True
    )

    health_chart = px.bar(
        health_data,
        x="resource_id",
        y=["cpu_usage", "memory_usage"],
        barmode="group",
        title="CPU and Memory Utilization (%)",
        labels={
            "resource_id": "Cloud Resource",
            "value": "Usage (%)",
            "variable": "Metric"
        }
    )

    st.plotly_chart(health_chart, width="stretch")
else:
    st.warning("Required CPU, memory, or resource ID columns are missing.")

# PDF Report Download
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
)
from reportlab.lib.styles import getSampleStyleSheet

st.subheader("Download PDF Report")

def create_pdf_report():
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(
        Paragraph("Cloud FinOps Optimization Report", styles["Title"])
    )
    elements.append(Spacer(1, 16))
    elements.append(
        Paragraph(
            "Summary of cloud resource costs and optimization analysis.",
            styles["Normal"]
        )
    )
    elements.append(Spacer(1, 16))

    pdf_data = [
        ["Resource ID", "Monthly Cost (Rs.)", "Recommendation"]
    ]

    for _, row in results.iterrows():
        pdf_data.append([
            str(row.get("resource_id", "")),
            f'{float(row.get("monthly_cost", 0)):,.0f}',
            str(row.get("recommendation", "Review"))
        ])

    table = Table(pdf_data, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#243b53")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [colors.white, colors.whitesmoke]),
    ]))

    elements.append(table)
    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()

pdf_bytes = create_pdf_report()

st.download_button(
    label="Download PDF Report",
    data=pdf_bytes,
    file_name="cloud_finops_report.pdf",
    mime="application/pdf"
)
