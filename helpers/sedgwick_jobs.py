import os
import json
import time
import tempfile
from typing import List, Dict, Optional
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException


SEDGWICK_URL = "https://www.sedgwick.com/careers/"
SEARCH_KEYWORD = "Housing Coordinator"


def extract_job_details(driver, job_url: str) -> Optional[Dict]:
    """Navigate to a job posting URL and extract detailed information"""
    try:
        driver.get(job_url)
        time.sleep(3)
        
        wait = WebDriverWait(driver, 15)
        
        job_details = {
            'url': job_url,
            'title': '',
            'apply_button_url': '',
            'locations': [],
            'time_type': '',
            'posted_date': '',
            'job_id': '',
            'full_description': '',
        }
        
        # Extract job title
        try:
            title_element = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "h2[data-automation-id='jobPostingHeader']"))
            )
            job_details['title'] = title_element.text
        except:
            pass
        
        # Extract Apply button URL
        try:
            apply_button = driver.find_element(By.CSS_SELECTOR, "a[data-automation-id='adventureButton']")
            job_details['apply_button_url'] = apply_button.get_attribute('href')
        except:
            pass
        
        # Extract all locations
        try:
            # Check for collapsed button and click it
            try:
                view_button = driver.find_element(By.CSS_SELECTOR, "button[data-automation-id='locationButton-collapsed']")
                driver.execute_script("arguments[0].scrollIntoView(true);", view_button)
                time.sleep(0.5)
                driver.execute_script("arguments[0].click();", view_button)
                time.sleep(2)
            except:
                pass
            
            # Extract all visible locations
            location_elements = driver.find_elements(By.CSS_SELECTOR, "div[data-automation-id='locations'] dd")
            all_locations = []
            
            for loc in location_elements:
                loc_text = loc.text.strip()
                if loc_text and not (loc_text.split()[0].isdigit() and "Location" in loc_text):
                    all_locations.append(loc_text)
            
            # Check for additional locations
            try:
                additional_locations = driver.find_elements(By.CSS_SELECTOR, "div[data-automation-id='additionalLocations'] dd")
                for loc in additional_locations:
                    loc_text = loc.text.strip()
                    if loc_text and not (loc_text.split()[0].isdigit() and "Location" in loc_text):
                        all_locations.append(loc_text)
            except:
                pass
            
            # Remove duplicates
            seen = set()
            for loc in all_locations:
                if loc not in seen:
                    seen.add(loc)
                    job_details['locations'].append(loc)
        except:
            pass
        
        # Extract time type
        try:
            time_type_element = driver.find_element(By.CSS_SELECTOR, "div[data-automation-id='time'] dd")
            job_details['time_type'] = time_type_element.text
        except:
            pass
        
        # Extract posted date
        try:
            posted_element = driver.find_element(By.CSS_SELECTOR, "div[data-automation-id='postedOn'] dd")
            job_details['posted_date'] = posted_element.text
        except:
            pass
        
        # Extract job ID
        try:
            job_id_element = driver.find_element(By.CSS_SELECTOR, "div[data-automation-id='requisitionId'] dd")
            job_details['job_id'] = job_id_element.text
        except:
            pass
        
        # Extract full job description
        try:
            description_element = driver.find_element(By.CSS_SELECTOR, "div[data-automation-id='jobPostingDescription']")
            job_details['full_description'] = description_element.text
        except:
            pass
        
        return job_details
        
    except Exception as e:
        return None


def scrape_sedgwick_jobs() -> List[Dict]:
    """Main scraping function that returns list of job details"""
    chrome_options = Options()
    chrome_options.binary_location = "/usr/bin/google-chrome" # comment this for windows
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument(f"--user-data-dir={tempfile.mkdtemp()}")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), 
        options=chrome_options
    )
    
    try:
        driver.get(SEDGWICK_URL)
        wait = WebDriverWait(driver, 15)
        
        # Handle cookie banner
        try:
            accept_cookies = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Accept All Cookies')]"))
            )
            accept_cookies.click()
            time.sleep(2)
        except TimeoutException:
            pass
        
        # Click Join us button
        join_button = None
        selectors = [
            (By.LINK_TEXT, "Join us"),
            (By.XPATH, "//a[contains(text(), 'Join us')]"),
        ]
        
        for by, selector in selectors:
            try:
                join_button = wait.until(EC.element_to_be_clickable((by, selector)))
                break
            except TimeoutException:
                continue
        
        if not join_button:
            return []
        
        join_url = join_button.get_attribute('href')
        if join_url:
            driver.get(join_url)
            time.sleep(5)
        else:
            driver.execute_script("arguments[0].click();", join_button)
            time.sleep(5)
        
        # Handle second cookie banner
        try:
            accept_cookies_selectors = [
                (By.CSS_SELECTOR, "button[data-automation-id='legalNoticeAcceptButton']"),
                (By.XPATH, "//button[@data-automation-id='legalNoticeAcceptButton']"),
            ]
            
            for by, selector in accept_cookies_selectors:
                try:
                    accept_cookies_2 = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((by, selector))
                    )
                    try:
                        accept_cookies_2.click()
                    except:
                        driver.execute_script("arguments[0].click();", accept_cookies_2)
                    time.sleep(3)
                    break
                except TimeoutException:
                    continue
        except:
            pass
        
        # Find search input
        search_input = None
        input_selectors = [
            (By.CSS_SELECTOR, "input[data-automation-id='keywordSearchInput']"),
            (By.CSS_SELECTOR, "input[placeholder='Search for jobs or keywords']"),
        ]
        
        for by, selector in input_selectors:
            try:
                search_input = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((by, selector))
                )
                break
            except TimeoutException:
                continue
        
        if not search_input:
            return []
        
        driver.execute_script("arguments[0].scrollIntoView(true);", search_input)
        time.sleep(1)
        search_input.clear()
        search_input.click()
        time.sleep(0.5)
        search_input.send_keys(SEARCH_KEYWORD)
        time.sleep(1)
        
        # Click search button
        search_button = None
        button_selectors = [
            (By.CSS_SELECTOR, "button[data-automation-id='keywordSearchButton']"),
            (By.XPATH, "//button[@data-automation-id='keywordSearchButton']"),
        ]
        
        for by, selector in button_selectors:
            try:
                search_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((by, selector))
                )
                break
            except TimeoutException:
                continue
        
        if not search_button:
            return []
        
        search_button.click()
        time.sleep(5)
        
        # Extract job listings
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "li.css-1q2dra3"))
            )
        except TimeoutException:
            return []
        
        job_items = driver.find_elements(By.CSS_SELECTOR, "li.css-1q2dra3")
        jobs_data = []
        
        for job_item in job_items:
            try:
                title_element = job_item.find_element(By.CSS_SELECTOR, "a[data-automation-id='jobTitle']")
                job_url = title_element.get_attribute('href')
                
                if job_url:
                    jobs_data.append({'url': job_url})
            except:
                continue
        
        # Extract detailed information for each job
        detailed_jobs = []
        
        for job in jobs_data:
            job_details = extract_job_details(driver, job['url'])
            if job_details:
                detailed_jobs.append(job_details)
            time.sleep(2)
        
        return detailed_jobs
        
    except Exception as e:
        return []
    finally:
        driver.quit()



