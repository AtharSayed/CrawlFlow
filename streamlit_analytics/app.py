import json
from pathlib import Path

import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------------------------------------
# Page Config
# -------------------------------------------------
st.set_page_config(
    page_title="Website Crawler Analytics",
    layout="wide",
)

# -------------------------------------------------
# Paths
# -------------------------------------------------
METRICS_PATH = Path("/data/metrics/summary.json")

# -------------------------------------------------
# Load data
# -------------------------------------------------
def load_summary(path: Path):
    if not path.exists():
        st.error("❌ summary.json not found. Run the Airflow pipeline first.")
        st.stop()
    with open(path, "r") as f:
        return json.load(f)


summary = load_summary(METRICS_PATH)

# -------------------------------------------------
# Custom CSS
# -------------------------------------------------
st.markdown(
    """
    <style>
        .dashboard-title {
            text-align: center;
            font-size: 42px;
            font-weight: 700;
            margin-bottom: 0.25em;
        }
        .dashboard-subtitle {
            text-align: center;
            font-size: 16px;
            color: #6b7280;
            margin-bottom: 2em;
        }
        .kpi-box {
            padding: 1.2em;
            border-radius: 12px;
            background-color: #f9fafb;
            border: 1px solid #e5e7eb;
            text-align: center;
        }
        .kpi-value {
            font-size: 32px;
            font-weight: 700;
            color: #111827;   /* Dark slate (high contrast on white cards) */
        }
        .kpi-label {
            font-size: 14px;
            color: #6b7280;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------------------------------------
# Header
# -------------------------------------------------
st.markdown(
    """
    <div class="dashboard-title">🌐 Website Crawler Analytics</div>
    <div class="dashboard-subtitle">
        End-to-end analytics dashboard powered by Airflow
    </div>
    """,
    unsafe_allow_html=True,
)

# -------------------------------------------------
# KPI Section
# -------------------------------------------------
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        f"""
        <div class="kpi-box">
            <div class="kpi-value">{summary["total_websites_processed"]}</div>
            <div class="kpi-label">Total Websites</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        f"""
        <div class="kpi-box">
            <div class="kpi-value">{summary["active_websites"]}</div>
            <div class="kpi-label">Active Websites</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        f"""
        <div class="kpi-box">
            <div class="kpi-value">{summary["inactive_websites"]}</div>
            <div class="kpi-label">Inactive Websites</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col4:
    st.markdown(
        f"""
        <div class="kpi-box">
            <div class="kpi-value">{summary["num_websites_with_case_studies"]}</div>
            <div class="kpi-label">Case Studies Found</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# -------------------------------------------------
# Content Length Stats
# -------------------------------------------------
st.markdown("## 📊 Content Length Statistics")
st.markdown(
    "<p style='color:#6b7280;'>Summary of extracted content across website sections</p>",
    unsafe_allow_html=True,
)

rows = []
for section, stats in summary["content_length_stats"].items():
    rows.append(
        {
            "Section": section.capitalize(),
            "Min Length": stats["min"],
            "Max Length": stats["max"],
            "Average Length": round(stats["avg"], 2),
            "Count": stats["count"],
        }
    )

df = pd.DataFrame(rows)

st.dataframe(
    df,
    use_container_width=True,
    hide_index=True,
)

# -------------------------------------------------
# Visualizations
# -------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    fig_avg = px.bar(
        df,
        x="Section",
        y="Average Length",
        title="Average Content Length by Section",
        text="Average Length",
        template="plotly_white",
    )
    fig_avg.update_layout(
        title_x=0.5,
        height=420,
    )
    st.plotly_chart(fig_avg, use_container_width=True)

with col2:
    fig_range = px.bar(
        df,
        x="Section",
        y=["Min Length", "Max Length"],
        title="Content Length Range by Section",
        barmode="group",
        template="plotly_white",
    )
    fig_range.update_layout(
        title_x=0.5,
        height=420,
    )
    st.plotly_chart(fig_range, use_container_width=True)

# -------------------------------------------------
# Metadata / Engineering Info
# -------------------------------------------------
with st.expander("ℹ️ Pipeline Metadata"):
    st.write(f"**Aggregation Timestamp:** {summary['aggregation_timestamp']}")
    st.write("**Orchestrator:** Apache Airflow")
    st.write("**Analytics Layer:** Streamlit")
    st.write("**Data Contract:** File-based (`summary.json`)")
    st.write("**Scalability:** Config-driven ingestion + dynamic task mapping")

# -------------------------------------------------
# Footer
# -------------------------------------------------
st.markdown(
    """
    <hr/>
    <div style="text-align:center; color:#9ca3af; font-size:13px;">
        Built with Streamlit • Orchestrated by Airflow • Designed for scalable analytics
    </div>
    """,
    unsafe_allow_html=True,
)
