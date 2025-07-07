import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="CareerCraft Application Tracker", layout="wide")
st.title("Application Tracker")

CSV_FILE = "applications.csv"

# Load or create the CSV file
if os.path.exists(CSV_FILE):
    df = pd.read_csv(CSV_FILE)
else:
    df = pd.DataFrame(columns=[
        "Status", "Company", "Job Title", "Job Type", "On-site/Remote",
        "Salary", "Location", "Date Applied", "Link to Posting", "Interest in Role"
    ])
    df.to_csv(CSV_FILE, index=False)

# Create two columns: Table (left), Form (right)
col1, col2 = st.columns([2, 1])  # Wider left column for table

# --- LEFT: Editable Table ---
with col1:
    st.markdown("### Application History")

    # Add delete column
    df["Delete?"] = False

    edited_df = st.data_editor(
        df,
        num_rows="dynamic",
        use_container_width=True,
        height=450,
        column_config={
            "Delete?": st.column_config.CheckboxColumn(required=False),
        },
        disabled=[]  # All columns editable
    )

    # Save & Delete buttons
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("Save Changes"):
            df_clean = edited_df.drop(columns=["Delete?"], errors="ignore")
            df_clean.to_csv(CSV_FILE, index=False)
            st.success("Changes saved.")

    with col_btn2:
        if st.button("Delete Selected"):
            df = edited_df[edited_df["Delete?"] == False].drop(columns=["Delete?"], errors="ignore")
            df.to_csv(CSV_FILE, index=False)
            st.success("Selected rows deleted.")

# --- RIGHT: Add New Application Form ---
with col2:
    st.markdown("### Add New Application")
    with st.form("add_form", clear_on_submit=True):
        status = st.selectbox("Status", ["Not Applied", "Applied", "Interviewing", "Rejected", "Offer"])
        company = st.text_input("Company")
        job_title = st.text_input("Job Title")
        job_type = st.selectbox("Job Type", ["Full-time", "Internship", "Part-time", "Contract", "Other"])
        location_type = st.selectbox("On-site/Remote", ["On-site", "Remote", "Hybrid"])
        salary = st.text_input("Salary (optional)")
        location = st.text_input("Location")
        date_applied = st.date_input("Date Applied")
        link = st.text_input("Link to Posting")
        interest = st.select_slider("Interest in Role (1–5)", options=["1", "2", "3", "4", "5"])

        submitted = st.form_submit_button("Add Entry")
        if submitted:
            new_entry = pd.DataFrame([{
                "Status": status,
                "Company": company,
                "Job Title": job_title,
                "Job Type": job_type,
                "On-site/Remote": location_type,
                "Salary": salary,
                "Location": location,
                "Date Applied": date_applied,
                "Link to Posting": link,
                "Interest in Role": interest
            }])
            df = pd.concat([df.drop(columns=["Delete?"], errors="ignore"), new_entry], ignore_index=True)
            df.to_csv(CSV_FILE, index=False)
            st.success(f"Added: {company} – {job_title}")