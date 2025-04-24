import configparser
import os
import re

import pandas as pd
from apify_client import ApifyClient


# Function to clean job descriptions
def clean_job_description(text):
    # Remove HTML tags
    text = re.sub(r"<.*?>", " ", text)
    # Replace multiple spaces/newlines with a single space
    text = re.sub(r"\s+", " ", text).strip()
    return text


def scrape_indeed(job_title, location, num_jobs, remote_option, date_posted, job_type):
    # Initialize ConfigParser
    config = configparser.ConfigParser()

    config_file_path = os.path.abspath("Resources/config.ini")

    # Read the config.ini file
    config.read(config_file_path)

    # Initialize the ApifyClient with your API token
    apify_api_key = config["DEFAULT"]["APIFY_API_KEY"]
    client = ApifyClient(apify_api_key)

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

    # Run the Actor and wait for it to finish
    run = client.actor("canadesk/indeed-linkedin").call(run_input=run_input)

    data = [item for item in client.dataset(run["defaultDatasetId"]).iterate_items()]
    df = pd.DataFrame(data)

    # Selecting required columns and renaming them
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

    # Apply cleaning function to 'Job Description' column
    jobs_data['Job Description'] = jobs_data['Job Description'].apply(clean_job_description)

    return jobs_data
