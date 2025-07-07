import streamlit as st
import pandas as pd
import altair as alt
import os

st.set_page_config(page_title="CareerCraft Homepage", layout="wide")
st.title("CareerCraft")
st.markdown("*Shape your story. Craft your future.*")

CSV_FILE = "applications.csv"

# Load data
if os.path.exists(CSV_FILE):
    df = pd.read_csv(CSV_FILE)
else:
    st.info("No data yet. Add job applications from the tracker.")
    st.stop()

# Summary Stats
total_jobs = len(df)
total_applied = len(df[df["Status"].isin(["Applied", "Interviewing", "Offer", "Rejected"])])
total_offers = len(df[df["Status"] == "Offer"])
total_interviewing = len(df[df["Status"] == "Interviewing"])

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Jobs", total_jobs)
col2.metric("Applied", total_applied)
col3.metric("Interviewing", total_interviewing)
col4.metric("Offers", total_offers)

st.markdown("---")

# Charts Section - Side by Side
st.markdown("### Application Insights")

chart_col1, chart_col2 = st.columns(2)

#Chart 1: Status Distribution (Bar Chart)
with chart_col1:
    st.markdown("**Status Distribution**")
    status_count = df["Status"].value_counts().reset_index()
    status_count.columns = ["Status", "Count"]

    bar_chart = alt.Chart(status_count).mark_bar().encode(
        x=alt.X("Status", sort="-y"),
        y="Count",
        color="Status",
        tooltip=["Status", "Count"]
    ).properties(height=300)

    st.altair_chart(bar_chart, use_container_width=True)

# Chart 2: Applications Over Time (Line Chart)
with chart_col2:
    st.markdown("**Applications Over Time**")
    df["Date Applied"] = pd.to_datetime(df["Date Applied"], errors='coerce')
    daily_counts = df.groupby(df["Date Applied"].dt.date).size().reset_index(name="Applications")

    line_chart = alt.Chart(daily_counts).mark_line(point=True).encode(
        x="Date Applied:T",
        y="Applications:Q",
        tooltip=["Date Applied", "Applications"]
    ).properties(height=300)

    st.altair_chart(line_chart, use_container_width=True)

