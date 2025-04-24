import os
import pickle
import time

import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from utilities.chromedriver_launch import launch_driver


def scrape_linkedin(job_title, location, num_jobs, remote_option, date_posted, job_type):
    driver = launch_driver()

    driver.get("https://www.linkedin.com/")

    linkedin_cookies = os.path.abspath("linkedin_cookies.pkl")

    cookies = pickle.load(open(linkedin_cookies, "rb"))
    for cookie in cookies:
        driver.add_cookie(cookie)

    driver.get("https://www.linkedin.com/jobs/")
    time.sleep(3)

    wait = WebDriverWait(driver, 10)

    search_box = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//input[@aria-label='Search by title, skill, or company']"))
    )
    search_box.click()
    search_box.send_keys(job_title)
    search_box.send_keys(Keys.ENTER)

    location_input = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//input[@aria-label='City, state, or zip code']"))
    )
    location_input.click()
    location_input.clear()
    location_input.send_keys(location)
    location_input.send_keys(Keys.ENTER)

    # all filters
    driver.find_element(By.XPATH,
                        "//button[@aria-label='Show all filters. Clicking this button displays all available filter options.']").click()
    time.sleep(2)
    driver.find_element(By.XPATH, f"//label[contains(., '{date_posted}')]").click()
    driver.find_element(By.XPATH, f"//label[contains(., '{job_type}')]").click()
    if remote_option:
        driver.find_element(By.XPATH, f"//label[contains(., 'Remote')]").click()
    time.sleep(2)
    driver.find_element(By.XPATH, "//button[@data-test-reusables-filters-modal-show-results-button='true']").click()

    jobs_list = extract_jobs(driver, num_jobs)
    jobs_data = pd.DataFrame(jobs_list,
                             columns=['Platform', 'Job Title', 'Company', 'Location', 'Job Description', 'Job URL'])
    driver.quit()
    return jobs_data


def extract_jobs(driver, num_jobs):
    time.sleep(3)
    jobs = driver.find_elements(By.XPATH, "/html/body/div[6]/div[3]/div[4]/div/div/main/div/div[2]/div[1]/div/ul/li")

    job_data = []
    for job in jobs[:num_jobs]:
        try:
            time.sleep(1)
            title_element = job.find_element(By.XPATH, ".//a/span[@aria-hidden]")
            title = title_element.get_attribute("textContent").strip()
            company_element = job.find_element(By.XPATH,
                                               ".//div[@class='artdeco-entity-lockup__subtitle ember-view']//span[@dir='ltr']")
            company = company_element.get_attribute("textContent").strip()
            location_element = job.find_element(By.XPATH,
                                                ".//div[@class='artdeco-entity-lockup__caption ember-view']//span[@dir='ltr']")
            location = location_element.get_attribute("textContent").strip()
            job_id_element = job.find_element(By.XPATH, ".//div[@data-job-id]")
            job_id = job_id_element.get_attribute("data-job-id")
            job_url = f"https://www.linkedin.com/jobs/view/{job_id}"
            job.find_element(By.XPATH, ".//a").click()
            driver.execute_script("arguments[0].scrollIntoView();", job)

            job_description = driver.find_element(By.XPATH, "//div[@class='mt4']/p").get_attribute(
                "textContent").strip()

            # Append as a dictionary instead of list
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
