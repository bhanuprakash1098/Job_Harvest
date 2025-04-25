import configparser
import os
import re

import pandas as pd
from apify_client import ApifyClient


# --------------------------------------------
# Function to clean job descriptions:
# - Removes HTML tags
# - Collapses multiple spaces and newlines
# --------------------------------------------
def clean_job_description(text):
    # Remove HTML tags
    text = re.sub(r"<.*?>", " ", text)
    # Replace multiple spaces/newlines with a single space
    text = re.sub(r"\s+", " ", text).strip()
    return text


# --------------------------------------------
# Main function to scrape jobs from Indeed via Apify
# Parameters:
# - job_title: Title of the job to search
# - location: City or region
# - num_jobs: Max number of jobs to scrape
# - remote_option: Whether to include remote jobs
# - date_posted: Filter based on date
# - job_type: Full-time, Part-time, etc.
# --------------------------------------------
def scrape_indeed(job_title, location, num_jobs, remote_option, date_posted, job_type):
    # --------------------------------------------
    # STEP 1: Load API Key from config.ini
    # --------------------------------------------
    config = configparser.ConfigParser()
    config_file_path = os.path.abspath("Resources/config.ini")
    config.read(config_file_path)
    apify_api_key = config["DEFAULT"]["APIFY_API_KEY"]
    # --------------------------------------------
    # STEP 2: Initialize Apify client with API key
    # --------------------------------------------
    client = ApifyClient(apify_api_key)

    # --------------------------------------------
    # STEP 3: Define input mappings for API filters
    # --------------------------------------------
    job_type_mapping = {
        "Full-time": "fulltime",
        "Part-time": "parttime",
        "Internship": "internship",
        "Contract": "contract"
    }

    date_posted_mapping = {
        "Any time": "all",
        "Past 24 hours": "24h",
        "Past week": "48h",
        "Past month": "72h",
    }

    # --------------------------------------------
    # STEP 4: Prepare input for Apify actor run
    # - Uses "canadesk/indeed-linkedin" actor
    # --------------------------------------------
    # Prepare the Actor input
    run_input = {
        "city": location,
        "country": "USA",
        "title": job_title,
        "engines": "1",  # 1 for indeed and 2 for LinkedIn
        "jobtype": job_type_mapping.get(job_type, ""),
        "last": date_posted_mapping.get(date_posted, ""),
        # "distance": "50",
        "remote": remote_option,
        "max": num_jobs,
        "proxy": {
            "useApifyProxy": True
        }
    }

    # --------------------------------------------
    # STEP 5: Run the actor and fetch results
    # --------------------------------------------
    run = client.actor("canadesk/indeed-linkedin").call(run_input=run_input)

    data = [item for item in client.dataset(run["defaultDatasetId"]).iterate_items()]
    df = pd.DataFrame(data)

    # --------------------------------------------
    # STEP 6: Clean and format the data
    # - Select relevant columns
    # - Rename them to standard format
    # - Clean job descriptions
    # --------------------------------------------
    jobs_data = df[['title', 'company', 'location', 'description', 'job_url']].rename(
        columns={
            'title': 'Job Title',
            'company': 'Company',
            'location': 'Location',
            'description': 'Job Description',
            'job_url': 'Job URL'
        }
    )

    jobs_data['Platform'] = 'Indeed'

    # --------------------------------------------
    # STEP 7: Return the final cleaned DataFrame
    # --------------------------------------------
    jobs_data['Job Description'] = jobs_data['Job Description'].apply(clean_job_description)

    return jobs_data
