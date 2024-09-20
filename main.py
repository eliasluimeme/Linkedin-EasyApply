from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
import time
import re
import json
from selenium.webdriver.safari.options import Options as SafariOptions
from selenium.webdriver.safari.service import Service as SafariService
import csv
from datetime import datetime
import os

class EasyApplyLinkedin:

    def __init__(self, data):
        """Parameter initialization"""
        self.email = data['email']
        self.password = data['password']
        self.keywords = data['keywords']
        self.location = data['location']
        safari_options = SafariOptions()
        service = SafariService(executable_path=data['driver_path'])
        self.driver = webdriver.Safari(service=service, options=safari_options)
        self.wait = WebDriverWait(self.driver, 20)  # Increased wait time
        self.num_applications = data['num_applications']
        self.applications_submitted = 0

    def login_linkedin(self):
        """This function logs into your personal LinkedIn profile"""
        self.driver.get("https://www.linkedin.com/login")
        
        try:
            # Wait for the page to fully load
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            print("Login page fully loaded")

            # Wait for the email field to be clickable
            login_email = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "username"))
            )
            login_email.clear()
            login_email.send_keys(self.email)
            print("Email entered")
            
            # Wait for the password field to be clickable
            login_pass = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "password"))
            )
            login_pass.clear()
            login_pass.send_keys(self.password)
            print("Password entered")
            
            # Wait for the sign-in button to be clickable
            sign_in_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
            )
            sign_in_button.click()
            print("Sign-in button clicked")

        except TimeoutException:
            print("Timeout waiting for login page elements")
            return

        # Wait for the login process to complete
        try:
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.ID, "global-nav"))
            )
            print("Successfully logged in")
        except TimeoutException:
            print("Timeout waiting for login to complete")
            print("Please check if you're logged in correctly.")
            input("Press Enter to continue if you're logged in, or Ctrl+C to exit...")

    def job_search(self):
        """This function goes to the 'Jobs' section and looks for all the jobs that match the keywords and location"""
        try:
            # Navigate directly to the Jobs page
            self.driver.get("https://www.linkedin.com/jobs/")
            print("Navigated to Jobs page")
        except Exception as e:
            print(f"Error navigating to Jobs page: {e}")
            return

        try:
            # Wait for the search input fields to be present
            search_keywords = self.wait.until(EC.presence_of_element_located((By.XPATH, "//input[contains(@class, 'jobs-search-box__text-input') and contains(@id, 'jobs-search-box-keyword-id-')]")))
            search_location = self.wait.until(EC.presence_of_element_located((By.XPATH, "//input[contains(@class, 'jobs-search-box__text-input') and contains(@id, 'jobs-search-box-location-id-')]")))

            # Clear existing text and enter new search criteria
            search_keywords.clear()
            search_keywords.send_keys(self.keywords)
            print(f"Entered keywords: {self.keywords}")

            search_location.clear()
            search_location.send_keys(self.location)
            print(f"Entered location: {self.location}")

            # Wait for a few seconds after entering location
            time.sleep(3)
            print("Waited 3 seconds after entering location")

            # Submit the search by pressing Enter
            search_location.send_keys(Keys.RETURN)
            print("Pressed Enter to submit search")

            # Wait for results to load
            self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "jobs-search-results-list")))
            print("Search results loaded")

        except TimeoutException:
            print("Timeout: Couldn't find the search inputs or results. The page structure might have changed.")
        except Exception as e:
            print(f"An error occurred during job search: {e}")

    def filter(self):
        """This function filters all the job results by 'Easy Apply'"""
        try:
            # Wait for the page to fully load after the initial search
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.CLASS_NAME, "jobs-search-results-list"))
            )
            print("Search results page fully loaded")

            # Click on "All filters" button
            all_filters_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'search-reusables__filter-pill-button') and contains(., 'All filters')]")))
            all_filters_button.click()
            print("Clicked on 'All filters' button")

            # Wait for the filter modal to appear
            self.wait.until(EC.visibility_of_element_located((By.XPATH, "//h2[text()='All filters']")))
            print("Filter modal opened")

            # Find and click the "Easy Apply" toggle
            easy_apply_toggle = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//label[contains(@for, 'adToggle_ember') and .//span[contains(text(), 'Toggle Easy Apply filter')]]")))
            easy_apply_toggle.click()
            print("Toggled 'Easy Apply' filter")

            # Click on "Show results" button
            show_results_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'search-reusables__secondary-filters-show-results-button')]")))
            show_results_button.click()
            print("Clicked 'Show results' button")

            # Wait for the results to reload
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.CLASS_NAME, "jobs-search-results-list"))
            )
            print("Filtered results loaded")

        except TimeoutException:
            print("Timeout: Couldn't find filter elements. The page structure might have changed.")
        except Exception as e:
            print(f"An error occurred during filtering: {e}")

    def find_offers(self):
        """This function finds all the offers through all the pages result of the search and filter"""
        try:
            total_results = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "jobs-search-results-list__title-heading")))
            total_results_text = total_results.text.strip()
            if total_results_text:
                total_results_int = int(re.sub(r'[^\d]', '', total_results_text))
                print(f"Total results: {total_results_int}")
            else:
                print("Couldn't find total results, proceeding with available jobs")
                total_results_int = 0

            time.sleep(2)
            current_page = self.driver.current_url
            results = self.driver.find_elements(By.CLASS_NAME, "jobs-search-results__list-item")

            for result in results:
                if self.applications_submitted >= self.num_applications:
                    print(f"Reached the maximum number of applications ({self.num_applications})")
                    return

                hover = ActionChains(self.driver).move_to_element(result)
                hover.perform()
                titles = result.find_elements(By.CLASS_NAME, 'job-card-list__title')
                for title in titles:
                    try:
                        self.submit_apply(title)
                        self.applications_submitted += 1
                        if self.applications_submitted >= self.num_applications:
                            return
                    except Exception as e:
                        print(f"Error processing job: {e}")
                        continue

            # Remove pagination logic for simplicity, since we're limiting applications

        except Exception as e:
            print(f"An error occurred while finding offers: {e}")

    def submit_apply(self, job_add):
        """This function submits the application for the job add found"""
        print('Processing the position of: ', job_add.text)
        job_add.click()
        time.sleep(2)
        
        try:
            # Wait for the job details to load
            self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "jobs-search__job-details--container")))
            
            # Extract job details
            job_title = self.driver.find_element(By.CLASS_NAME, "job-details-jobs-unified-top-card__job-title").text
            company_name = self.driver.find_element(By.CLASS_NAME, "job-details-jobs-unified-top-card__company-name").text
            location = self.driver.find_element(By.CLASS_NAME, "job-details-jobs-unified-top-card__primary-description-container").text
            # posted_date = self.driver.find_element(By.CLASS_NAME, "jobs-unified-top-card__posted-date").text
            # applicants = self.driver.find_element(By.CLASS_NAME, "jobs-unified-top-card__applicant-count").text
            job_description = self.driver.find_element(By.CLASS_NAME, "jobs-description__content").text
            
            # Save job information before attempting to apply
            self.save_job_info(job_title, company_name, location, job_description)

            # Click the Apply button
            apply_button = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "jobs-apply-button")))
            apply_button.click()
            print(f"Clicked Apply button for: {job_title}")
            
            # Wait for the application form to load (you may need to adjust this depending on the actual application process)
            time.sleep(5)
            
            # Here you would add code to fill out the application form
            # This will depend on the specific structure of the form
            
        except NoSuchElementException:
            print('Application button not found. You may have already applied to this job.')
        except Exception as e:
            print(f'An error occurred while processing the job: {str(e)}')
        finally:
            # Ensure we save job info even if there's an error
            if 'job_title' in locals():
                self.save_job_info(job_title, company_name, location, job_description)
            else:
                print("Could not extract job details to save")

    def save_job_info(self, title, company, location, description):
        """Save job information to a CSV file"""
        try:
            filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'processed_jobs.csv')
            file_exists = os.path.isfile(filename)
            
            print(f"Attempting to save job info to: {filename}")
            
            with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['Date Processed', 'Job Title', 'Company', 'Location', 'Description']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                if not file_exists:
                    writer.writeheader()
                    print("Created new CSV file with header")
                
                print("LOCATION: ", location)
                writer.writerow({
                    'Date Processed': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'Job Title': title,
                    'Company': company,
                    'Location': location,
                    # 'Date Posted': date,
                    # 'Applicants': applicants,
                    'Description': description[:500]  # Limit description to 500 characters
                })
            
            print(f"Successfully saved job information to {filename}")
        except IOError as e:
            print(f"IOError occurred while saving job info: {e}")
            print(f"Current working directory: {os.getcwd()}")
            print(f"File path attempted: {filename}")
        except Exception as e:
            print(f"An unexpected error occurred while saving job info: {e}")

    def close_session(self):
        """This function closes the actual session"""
        print('End of the session, see you later!')
        self.driver.quit()

    def apply(self):
        """Apply to job offers"""
        self.driver.maximize_window()
        self.login_linkedin()
        time.sleep(5)
        self.job_search()
        time.sleep(5)
        self.filter()
        time.sleep(2)
        self.find_offers()
        time.sleep(2)
        self.close_session()


if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, 'config.json')
    
    with open(config_path) as config_file:
        data = json.load(config_file)

    bot = EasyApplyLinkedin(data)
    bot.apply()