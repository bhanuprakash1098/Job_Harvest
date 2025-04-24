import pandas as pd
import streamlit as st
from pypdf import PdfReader

from utilities.gpt_parser import evaluate_job_matches
from utilities.indeed_scraper import scrape_indeed
from utilities.linkedin_scraper import scrape_linkedin

st.set_page_config(page_title="JobHarvest a Job Scraping Framework", layout="wide")

st.title("🔍 Job Scraping Framework")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Job Search Parameters")
    job_title = st.text_input("Job Title", placeholder="e.g., Software Engineer")

with col2:
    st.subheader("Location")
    location = st.text_input("Location", placeholder="e.g., New York")

with col3:
    st.subheader("Number of Jobs Per Website")
    num_jobs = st.number_input("Enter a range (e.g., 5-10)", min_value=5, max_value=50, value=5, step=1)

# Additional filters
st.subheader("Additional Filters")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Date Posted")
    date_posted = st.selectbox("Select timeframe",
                               ["Any time", "Past 24 hours", "Past week", "Past month"])

with col2:
    st.subheader("Remote")
    remote_option = st.selectbox("Remote Option", ["Yes", "No"])

with col3:
    st.subheader("Job Type")
    job_type = st.selectbox("Select Job Type",
                            ["Full-time", "Part-time", "Internship", "Contract"])

st.subheader("Select Job Platforms")
col1, col2 = st.columns(2)

platforms_selected = {
    "LinkedIn": col2.checkbox("LinkedIn", value=False),
    "Indeed": col1.checkbox("Indeed", value=False),
    # "Glassdoor": col3.checkbox("Glassdoor", value=False),
    # "Zip Recruiter": col4.checkbox("Zip Recruiter", value=False),
}

if st.button("Start Scraping"):
    selected_platforms = [platform for platform, selected in platforms_selected.items() if selected]

    if not selected_platforms:
        st.warning("Please select at least one platform.")
    elif not job_title or not location:
        st.warning("Please provide Job Title and Location.")
    else:
        st.success(f"Scraping Jobs from: {', '.join(selected_platforms)}")

        all_jobs_data = []
        for platform in selected_platforms:
            st.write(f"Scraping from {platform} for '{job_title}' in '{location}'")
            if platform == "LinkedIn":
                jobs_data = scrape_linkedin(job_title, location, num_jobs, remote_option, date_posted, job_type)
            elif platform == "Indeed":
                jobs_data = scrape_indeed(job_title, location, num_jobs, remote_option, date_posted, job_type)
            elif platform == "Glassdoor":
                jobs_data = scrape_glassdoor(job_title, location, num_jobs, remote_option, date_posted, job_type)
            elif platform == "Zip Recruiter":
                jobs_data = scrape_zip_recruiter(job_title, location, num_jobs, remote_option, date_posted, job_type)

            all_jobs_data.append(jobs_data)
        if all_jobs_data:
            jobs_data_combined = pd.concat(all_jobs_data, ignore_index=True)
            st.session_state.jobs_data = jobs_data_combined

            # **Display jobs in Streamlit before sending to GPT**
            st.subheader("🔍 Scraped Job Listings")
            st.dataframe(jobs_data_combined)  # Shows data in a scrollable table format


# Function to read different document types
def read_pdf(file):
    pdf_reader = PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() or ""
    return text.strip()


if "jobs_data" in st.session_state:
    st.subheader("Resume Analysis")
    uploaded_file = st.file_uploader("Upload Resume (PDF only)", type=["pdf"])

    if uploaded_file is not None:
        # Process PDF file
        resume_text = read_pdf(uploaded_file)

        if st.button("Evaluate Jobs"):
            if resume_text:
                st.write("Evaluating your resume with different job listings...")
                match_df = evaluate_job_matches(st.session_state.jobs_data, resume_text)
                st.dataframe(match_df)
            else:
                st.warning("Unable to extract text from the uploaded PDF.")
    else:
        st.info("Please upload a resume file in PDF format.")
