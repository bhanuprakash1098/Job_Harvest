import pandas as pd
import streamlit as st
from pypdf import PdfReader

from utilities.gpt_parser import evaluate_job_matches
from utilities.indeed_scraper import scrape_indeed
from utilities.linkedin_scraper import scrape_linkedin

# --------------------------------------------
# 🚀 Streamlit Page Configuration
# --------------------------------------------
st.set_page_config(page_title="JobHarvest a Job Scraping Framework", layout="wide")

st.title("🔍 Job Scraping Framework")

# --------------------------------------------
# 🔎 Input Filters: Job Title, Location, Job Count
# --------------------------------------------
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

# --------------------------------------------
# 🧰 Additional Job Filters: Date Posted, Remote, Job Type
# --------------------------------------------
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

# --------------------------------------------
# 🌐 Job Platform Selection (checkbox options)
# --------------------------------------------
st.subheader("Select Job Platforms")
col1, col2 = st.columns(2)

platforms_selected = {
    "LinkedIn": col2.checkbox("LinkedIn", value=False),
    "Indeed": col1.checkbox("Indeed", value=False),
    # Future integrations can be added below:
    # "Glassdoor": col3.checkbox("Glassdoor", value=False),
    # "Zip Recruiter": col4.checkbox("Zip Recruiter", value=False),
}

# --------------------------------------------
# 🚦 Scraping Button: Initiates the scraping process
# --------------------------------------------
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
            # Call appropriate scraper function based on selected platform
            if platform == "LinkedIn":
                jobs_data = scrape_linkedin(job_title, location, num_jobs, remote_option, date_posted, job_type)
            elif platform == "Indeed":
                jobs_data = scrape_indeed(job_title, location, num_jobs, remote_option, date_posted, job_type)

            all_jobs_data.append(jobs_data)
        # Combine all job data and save to session state
        if all_jobs_data:
            jobs_data_combined = pd.concat(all_jobs_data, ignore_index=True)
            st.session_state.jobs_data = jobs_data_combined

            # Display results before proceeding to resume evaluation
            st.subheader("🔍 Scraped Job Listings")
            st.dataframe(jobs_data_combined)  # Shows data in a scrollable table format


# --------------------------------------------
# 📄 PDF Reader Function to Extract Resume Text
# --------------------------------------------
def read_pdf(file):
    pdf_reader = PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() or ""
    return text.strip()

# --------------------------------------------
# 📈 Resume Analysis Section (After Jobs are Scraped)
# --------------------------------------------
if "jobs_data" in st.session_state:
    st.subheader("Resume Analysis")

    # File uploader for PDF resume
    uploaded_file = st.file_uploader("Upload Resume (PDF only)", type=["pdf"])

    if uploaded_file is not None:
        # Extract raw text from uploaded PDF resume
        resume_text = read_pdf(uploaded_file)

        if st.button("Evaluate Jobs"):
            if resume_text:
                st.write("Evaluating your resume with different job listings...")
                # Call GPT-based evaluation logic
                match_df = evaluate_job_matches(st.session_state.jobs_data, resume_text)
                # Display the match results as a table
                st.dataframe(match_df)
            else:
                st.warning("Unable to extract text from the uploaded PDF.")
    else:
        st.info("Please upload a resume file in PDF format.")
