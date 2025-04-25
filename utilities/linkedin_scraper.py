import os
import pickle
import time

import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from utilities.chromedriver_launch import launch_driver


# --------------------------------------------
# Scrapes job listings from LinkedIn using Selenium
# Applies filters: job title, location, job type, date posted, remote option
# Returns a DataFrame with structured job data
# --------------------------------------------
def scrape_linkedin(job_title, location, num_jobs, remote_option, date_posted, job_type):
    # Launch a headless Chrome driver instance
    driver = launch_driver()

    # Step 1: Go to LinkedIn login page
    driver.get("https://www.linkedin.com/")

    # Step 2: Load cookies to bypass login
    linkedin_cookies = os.path.abspath("linkedin_cookies.pkl")
    cookies = pickle.load(open(linkedin_cookies, "rb"))
    for cookie in cookies:
        driver.add_cookie(cookie)

    # Step 3: Navigate to LinkedIn Jobs page
    driver.get("https://www.linkedin.com/jobs/")
    time.sleep(3)
    wait = WebDriverWait(driver, 10)

    # Step 4: Search by job title
    search_box = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//input[@aria-label='Search by title, skill, or company']"))
    )
    search_box.click()
    search_box.send_keys(job_title)
    search_box.send_keys(Keys.ENTER)

    # Step 5: Input location and press Enter
    location_input = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//input[@aria-label='City, state, or zip code']"))
    )
    location_input.click()
    location_input.clear()
    location_input.send_keys(location)
    location_input.send_keys(Keys.ENTER)

    # Step 6: Open "All filters" panel
    driver.find_element(By.XPATH,
                        "//button[@aria-label='Show all filters. Clicking this button displays all available filter options.']").click()
    time.sleep(2)

    # Step 7: Apply date posted, job type, and remote filters
    driver.find_element(By.XPATH, f"//label[contains(., '{date_posted}')]").click()
    driver.find_element(By.XPATH, f"//label[contains(., '{job_type}')]").click()
    if remote_option:
        driver.find_element(By.XPATH, f"//label[contains(., 'Remote')]").click()
    time.sleep(2)

    # Step 8: Click "Show results" button to apply filters
    driver.find_element(By.XPATH, "//button[@data-test-reusables-filters-modal-show-results-button='true']").click()

    # Step 9: Extract the job results into a DataFrame
    jobs_list = extract_jobs(driver, num_jobs)
    jobs_data = pd.DataFrame(jobs_list,
                             columns=['Platform', 'Job Title', 'Company', 'Location', 'Job Description', 'Job URL'])

    # Step 10: Close browser session
    driver.quit()
    return jobs_data


# --------------------------------------------
# Helper function to extract job data from LinkedIn job cards
# Returns a list of dictionaries, each representing a job
# --------------------------------------------
def extract_jobs(driver, num_jobs):
    time.sleep(3)
    # Locate all job listing elements
    jobs = driver.find_elements(By.XPATH, "/html/body/div[6]/div[3]/div[4]/div/div/main/div/div[2]/div[1]/div/ul/li")

    job_data = []
    for job in jobs[:num_jobs]:  # Limit to desired number of jobs
        try:
            time.sleep(1)
            # Extract job title
            title_element = job.find_element(By.XPATH, ".//a/span[@aria-hidden]")
            title = title_element.get_attribute("textContent").strip()

            # Extract company name
            company_element = job.find_element(By.XPATH,
                                               ".//div[@class='artdeco-entity-lockup__subtitle ember-view']//span[@dir='ltr']")
            company = company_element.get_attribute("textContent").strip()

            # Extract location
            location_element = job.find_element(By.XPATH,
                                                ".//div[@class='artdeco-entity-lockup__caption ember-view']//span[@dir='ltr']")
            location = location_element.get_attribute("textContent").strip()

            # Generate job URL from job ID
            job_id_element = job.find_element(By.XPATH, ".//div[@data-job-id]")
            job_id = job_id_element.get_attribute("data-job-id")
            job_url = f"https://www.linkedin.com/jobs/view/{job_id}"

            # Click job to load full description
            job.find_element(By.XPATH, ".//a").click()
            driver.execute_script("arguments[0].scrollIntoView();", job)

            # Extract job description text
            job_description = driver.find_element(By.XPATH, "//div[@class='mt4']/p").get_attribute(
                "textContent").strip()

            # Append job data as dictionary
            job_data.append({
                "Platform": "LinkedIn",
                "Job Title": title,
                "Company": company,
                "Location": location,
                "Job Description": job_description,
                "Job URL": job_url
            })
        except Exception as e:
            print(f"Skipping job due to error: {e}")

    return job_data
