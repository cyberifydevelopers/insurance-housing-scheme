from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import requests
from bs4 import BeautifulSoup
import json
import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait, Select
import httpx
import tempfile
import asyncio 
from selenium.common.exceptions import TimeoutException
import os
import logging 
from helpers.logger_config import get_logger
logger = get_logger(__name__)
logging.disable(logging.CRITICAL)

# old code 
# async def job_scraper():
#     chrome_options = Options()
#     chrome_options.add_argument("--headless=new")
#     chrome_options.add_argument("--no-sandbox")
#     chrome_options.add_argument("--disable-dev-shm-usage")
#     chrome_options.add_argument(
#         f"--user-data-dir={tempfile.mkdtemp()}"
#     )  # unique profile

#     driver = webdriver.Chrome(
#         service=Service(ChromeDriverManager().install()), options=chrome_options
#     )
#     try:
#         url = "https://crsth.com/careers/"
#         driver.get(url)
#         wait = WebDriverWait(driver, 30)
#         iframe = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "iframe")))
#         driver.switch_to.frame(iframe)
#         jobs = []
#         seen_urls = set()
#         select_el = wait.until(
#             EC.presence_of_element_located(
#                 (By.CSS_SELECTOR, "select.countDropdown.browser-default")
#             )
#         )
#         select = Select(select_el)
#         option_values = [opt.get_attribute("value") for opt in select.options]
#         for value in option_values:
#             select_el = wait.until(
#                 EC.presence_of_element_located(
#                     (By.CSS_SELECTOR, "select.countDropdown.browser-default")
#                 )
#             )
#             select = Select(select_el)
#             select.select_by_value(value)
#             time.sleep(2)
#             parents = wait.until(
#                 EC.presence_of_all_elements_located(
#                     (By.CSS_SELECTOR, "li.jobInfo.JobListing")
#                 )
#             )
#             for parent in parents:
#                 try:
#                     title_el = parent.find_element(
#                         By.CSS_SELECTOR, "span.jobInfoLine.jobTitle"
#                     )
#                     url_el = parent.find_element(
#                         By.CSS_SELECTOR, "a.JobListing__container"
#                     )
#                     subtitle_el = parent.find_element(
#                         By.CSS_SELECTOR,
#                         "span.jobInfoLine.jobLocation.JobListing__subTitle",
#                     )
#                     desc_el = parent.find_element(
#                         By.CSS_SELECTOR, "span.jobInfoLine.jobDescription"
#                     )
#                     job_url = url_el.get_attribute("href")
#                     if job_url not in seen_urls:
#                         job = {
#                             "title": title_el.text.strip(),
#                             "url": job_url,
#                             "subtitle": subtitle_el.text.strip(),
#                             "description": desc_el.text.strip(),
#                         }
#                         jobs.append(job)
#                         seen_urls.add(job_url)
#                 except Exception as e:
#                     print("Error parsing job:", e)
#         return jobs
#     finally:
#         driver.quit()



async def job_scraper():
    chrome_options = Options()
    chrome_options.binary_location = "/usr/bin/google-chrome" # comment this for windows 
    chrome_options.add_argument("--headless=True")  # Uncomment for production
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument(f"--user-data-dir={tempfile.mkdtemp()}")
    

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), 
        options=chrome_options
    )
    
    driver.maximize_window()
    
    try:
        url = "https://crsth.com/careers/"
        # print(f"Loading {url}...")
        driver.get(url)
        
        # print("Waiting for iframe...")
        wait = WebDriverWait(driver, 30)
        iframe = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "iframe")))
        # print("✓ Found iframe")
        
        # print("Scrolling iframe into view...")
        driver.execute_script("arguments[0].scrollIntoView(true);", iframe)
        time.sleep(2)
        
        driver.switch_to.frame(iframe)
        # print("✓ Switched to iframe")
        
        # print("Waiting for loading spinner to disappear...")
        try:
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".portal-sprawl-loader-container"))
            )
            # print("  Loading spinner detected...")
            
            WebDriverWait(driver, 60).until(
                EC.invisibility_of_element_located((By.CSS_SELECTOR, ".portal-sprawl-loader-container"))
            )
            # print("✓ Loading spinner disappeared!")
            logger.info("Loading spinner disappeared.")
        except:
            # print("  No loading spinner found")
            pass 
        
        # print("Waiting for content to render...")
        # time.sleep(5)
        await asyncio.sleep(5)
        
        # Wait for job listings to appear
        # print("Waiting for job listings to load...")
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='/jobs/']"))
        )
        # print("✓ Job listings loaded!")
        
        # Check if there's a dropdown/filter
        # print("\nChecking for filters/dropdown...")
        all_selects = driver.find_elements(By.TAG_NAME, "select")
        
        jobs = []
        seen_urls = set()
        
        if all_selects:
            # If dropdown exists, iterate through options
            select_el = all_selects[0]
            # print(f"✓ Found dropdown with {len(Select(select_el).options)} options")
            
            select = Select(select_el)
            option_values = [opt.get_attribute("value") for opt in select.options]
            
            for idx, value in enumerate(option_values):
                # print(f"\n{'='*60}")
                # print(f"Processing filter {idx+1}/{len(option_values)}: '{value}'")
                # print(f"{'='*60}")

                
                
                # Re-select the option
                all_selects = driver.find_elements(By.TAG_NAME, "select")
                if all_selects:
                    select = Select(all_selects[0])
                    select.select_by_value(value)
                    # time.sleep(3)  # Wait for filtered results
                    await asyncio.sleep(5)
                
                # Scrape jobs for this filter
                jobs_found =await scrape_current_jobs(driver, seen_urls)
                jobs.extend(jobs_found)
                # print(f"  Found {len(jobs_found)} new jobs in this filter")
        else:
            # No dropdown, just scrape all visible jobs
            # print("No dropdown found, scraping all visible jobs...")
            jobs =await scrape_current_jobs(driver, seen_urls)
        
        # print(f"\n{'='*60}")
        # print(f"🎉 SCRAPING COMPLETE!")
        # print(f"{'='*60}")
        # print(f"Total unique jobs found: {len(jobs)}")
        logger.info(f"Total unique jobs found: {len(jobs)}")
        return jobs
        
    except Exception as e:
        # print(f"\n{'='*60}")
        # print(f"❌ ERROR OCCURRED")
        # print(f"{'='*60}")
        # print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        
        # driver.save_screenshot("error_screenshot.png")
        # print("\n📸 Screenshot saved")
        return []
        
    finally:
        # input("\n👉 Press Enter to close browser...")
        driver.quit()


async def scrape_current_jobs(driver, seen_urls):
    """Scrape all jobs currently visible on the page"""
    jobs = []
    
    # Find all job links
    job_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/jobs/']")
    
    # print(f"  Processing {len(job_links)} job listings...")
    
    for job_link in job_links:
        try:
            # Get the job URL
            job_url = job_link.get_attribute("href")
            
            # Skip if already processed
            if job_url in seen_urls:
                continue
            
            # Extract job title (h2 tag)
            try:
                title_el = job_link.find_element(By.CSS_SELECTOR, "h2[data-testid='typography']")
                title = title_el.text.strip()
            except:
                title = "No title"
            
            # Extract location (p tag with font-weight: 600)
            try:
                # Find p tag with specific style containing font-weight: 600
                location_els = job_link.find_elements(By.CSS_SELECTOR, "p[data-testid='typography']")
                location = "No location"
                for el in location_els:
                    style = el.get_attribute("style")
                    if "font-weight: 600" in style or "font-weight:600" in style:
                        location = el.text.strip()
                        break
            except:
                location = "No location"
            
            # Extract job type tag (e.g., "Full Time", "Hybrid")
            try:
                tag_el = job_link.find_element(By.CSS_SELECTOR, "div[data-testid*='-tag'] p")
                job_type = tag_el.text.strip()
            except:
                job_type = "Not specified"
            
            # Extract description (p tag with font-weight: normal, comes after the tag)
            try:
                # Find all p tags with data-testid='typography'
                all_p_tags = job_link.find_elements(By.CSS_SELECTOR, "p[data-testid='typography']")
                description = "No description"
                
                for p in all_p_tags:
                    style = p.get_attribute("style")
                    text = p.text.strip()
                    
                    # Look for p tag with font-weight: normal and has substantial text
                    if ("font-weight: normal" in style or "font-weight:normal" in style) and len(text) > 20:
                        description = text
                        break
                    # Fallback: if text is long and contains "..." it's likely the description
                    elif len(text) > 50 and ("..." in text or len(text) > 100):
                        description = text
                        break
                        
            except Exception as e:
                description = "No description"
                # print(f"      ⚠️  Description extraction error: {e}")
            
            job = {
                "title": title,
                "url": job_url,
                "location": location,
                "job_type": job_type,
                "description": description,
            }
            
            jobs.append(job)
            seen_urls.add(job_url)
            
            # print(f"    ✓ {title}")
            # print(f"      📍 {location}")
            # print(f"      🏷️  {job_type}")
            # print(f"      📝 {description[:80]}..." if len(description) > 80 else f"      📝 {description}")
            
        except Exception as e:
            # print(f"    ✗ Error parsing job: {e}")
            continue
    
    return jobs



async def _scrape_detail_page(driver, url):
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[-1])

    try:
        # print(f"      🔗 Loading: {url}")
        driver.get(url)

        wait = WebDriverWait(driver, 30)

        # Switch to iframe if present
        iframes = driver.find_elements(By.CSS_SELECTOR, "iframe")
        if iframes:
            wait.until(EC.frame_to_be_available_and_switch_to_it(iframes[0]))

        # Spinner handling
        try:
            wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".portal-sprawl-loader-container")
            ))
        except TimeoutException:
            pass

        try:
            wait.until(EC.invisibility_of_element_located(
                (By.CSS_SELECTOR, ".portal-sprawl-loader-container")
            ))
        except TimeoutException:
            pass

        salary =await  _extract_salary(driver)
        description =await _extract_section(driver, "Description")
        qualifications =await _extract_section(driver, "Qualifications")

        return {
            "salary": salary,
            "full_description": description,
            "qualifications": qualifications
        }

    except Exception as e:
        # print(f"      ❌ Detail scrape error: {e}")
        return {
            "salary": "Not provided",
            "full_description": [],
            "qualifications": []
        }

    finally:
        driver.close()
        driver.switch_to.window(driver.window_handles[0])



async def _extract_salary(driver):
    try:
        salary_el = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((
                By.XPATH,
                "//span[normalize-space()='Salary Range']/parent::div/following-sibling::div/span"
            ))
        )
        logger.info(f"      📊 Salary found: {salary_el.text.strip()}")
        return salary_el.text.strip()
    except Exception as e:
        # print(f"      ⚠️ Salary extraction failed: {e}")
        return "Not provided"


async def _extract_section(driver, section_title):
    try:
        section = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((
                By.XPATH,
                f"""
                //h2[normalize-space()='{section_title}']
                /following::div[.//p or .//li][1]
                """
            ))
        )
    except TimeoutException:
        # print(f"      ⚠️ {section_title} section not found")
        return []

    texts = []
    for el in section.find_elements(By.XPATH, ".//p | .//li"):
        txt = el.text.strip()
        if txt:
            texts.append(txt)

    # print(f"📄 {section_title}: {len(texts)} items")
    logger.info(f"📄 {section_title}: {len(texts)} items")
    return texts



async def enrich_jobs_with_details(jobs):
    """
    Receives the list produced by job_scraper() and augments every dict
    with salary + full_description_html by visiting the detail page.
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument(f"--user-data-dir={tempfile.mkdtemp()}")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )

    try:
        # print("\n============================================================")
        # print("🔍  STARTING DETAIL SCRAPE")
        # print("============================================================")

        for idx, job in enumerate(jobs, 1):
            # print(f"{idx:2d}/{len(jobs)}  {job['title'][:50]}…")
            extra =await _scrape_detail_page(driver, job["url"])
            job.update(extra)
        
        # print("\n✅ Detail scrape finished!")
        return jobs
    finally:
        driver.quit()

async def description_scraper(url):
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    job_title_div = soup.find("h1", {"class": "atsJobTitle"})
    job_title = job_title_div.text.strip() if job_title_div else None
    job_details = {}
    for field in [
        "Job Location",
        "Remote Type",
        "Position Type",
        "Salary Range",
        "Job Category",
    ]:
        div = soup.find("div", {"name": field})
        job_details[field.lower().replace(" ", "_")] = (
            div.find("span").text.strip() if div else None
        )
    job_description = {}
    desc_div = soup.find("span", {"name": "jobDesc"})
    if desc_div:
        paragraphs = [p.text.strip() for p in desc_div.find_all("p")]
        job_description["description"] = " ".join(paragraphs)
        job_description["responsibilities"] = [
            li.text.strip() for li in desc_div.find_all("li")
        ]
    qualifications_div = soup.find("div", {"name": "qualifications"})
    qualifications_list = []
    if qualifications_div:
        for li in qualifications_div.find_all("li"):
            qualifications_list.append(li.text.strip())
    data = {
        "job_title": job_title,
        "job_details": job_details,
        "job_description": job_description,
        "qualifications": qualifications_list,
    }

    return json.dumps(data, indent=4)


async def alacrity_jobs():
    url = "https://alacritysolutions.applytojob.com/apply/"
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    jobs = []
    for job_item in soup.find_all("li", class_="list-group-item"):
        a_tag = job_item.find("a")
        if not a_tag:
            continue
        title = a_tag.get_text(strip=True)
        link = a_tag["href"]
        location_tag = job_item.find("ul", class_="list-inline list-group-item-text")
        location = None
        if location_tag:
            li = location_tag.find("li")
            if li:
                location = li.get_text(strip=True).replace("\xa0", " ")
        jobs.append({"title": title, "link": link, "location": location})
    return jobs


async def alacrity_job_detail(job_url):
    url = job_url
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    job = {}
    title_tag = soup.select_one("#job-description strong")
    job["title"] = title_tag.get_text(strip=True) if title_tag else None
    company_tag = soup.select_one("#job-description p")
    job["company"] = company_tag.get_text(strip=True) if company_tag else None
    desc_paras = [
        p.get_text(" ", strip=True) for p in soup.select("#job-description p")
    ]
    job["description"] = " ".join(desc_paras)
    duties = (
        [
            li.get_text(strip=True)
            for li in soup.select("#job-description ul")[0].select("li")
        ]
        if soup.select("#job-description ul")
        else []
    )
    job["primary_duties"] = duties
    skills = (
        [
            li.get_text(strip=True)
            for li in soup.select("#job-description ul")[1].select("li")
        ]
        if len(soup.select("#job-description ul")) > 1
        else []
    )
    job["skills_requirements"] = skills
    supervisory = (
        [
            li.get_text(strip=True)
            for li in soup.select("#job-description ul")[2].select("li")
        ]
        if len(soup.select("#job-description ul")) > 2
        else []
    )
    job["supervisory_responsibilities"] = supervisory
    salary_tag = soup.find(string=lambda t: "salary" in t.lower())
    job["salary"] = salary_tag.strip() if salary_tag else None
    job_specifics = (
        [
            li.get_text(strip=True)
            for li in soup.select("#job-description ul")[3].select("li")
        ]
        if len(soup.select("#job-description ul")) > 3
        else []
    )
    job["job_specifics"] = job_specifics
    travel_required = (
        [
            li.get_text(strip=True)
            for li in soup.select("#job-description ul")[4].select("li")
        ]
        if len(soup.select("#job-description ul")) > 4
        else []
    )
    job["travel_required"] = travel_required
    benefits = (
        [
            li.get_text(strip=True)
            for li in soup.select("#job-description ul")[5].select("li")
        ]
        if len(soup.select("#job-description ul")) > 5
        else []
    )
    job["benefits"] = benefits
    return json.dumps(job, indent=2)



async def tacares_job_details():
    print(os.environ.get("SCRAPER_API_KEY"))
    url = "https://www.tacares.com/housing-support-specialist/"
    scraper_api_url = "http://api.scraperapi.com"
    params = {
        "api_key": os.environ.get("SCRAPER_API_KEY"),
        "url": url,
        "country_code": "us",
        "render": "false",     
    }

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Referer": "https://www.google.com/",
        "Connection": "keep-alive",
    }

    async with httpx.AsyncClient(follow_redirects=True, timeout=30.0, headers=headers) as client:
        response = await client.get(scraper_api_url, params=params)
        response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    content_div = soup.find("div", class_="bf-cpc-content")
    job_data = {}
    job_data["url"] = url

    if not content_div:
        return {"error": "Job content not found, maybe blocked"}

    title_tag = content_div.find("strong")
    if title_tag:
        job_data["title"] = title_tag.get_text(strip=True)

    department = content_div.find("strong", string="Department:")
    if department and department.next_sibling:
        job_data["department"] = department.next_sibling.strip()

    reports_to = content_div.find("strong", string="Reports to:")
    if reports_to and reports_to.next_sibling:
        job_data["reports_to"] = reports_to.next_sibling.strip()

    job_summary = content_div.find("strong", string="Job Summary")
    if job_summary:
        job_data["job_summary"] = (
            job_summary.find_parent("p")
            .get_text(" ", strip=True)
            .replace("Job Summary", "")
        )

    essential = content_div.find("strong", string="Essential Job Functions:")
    if essential:
        ul = essential.find_next("ul")
        if ul:
            job_data["essential_functions"] = [
                li.get_text(strip=True) for li in ul.find_all("li")
            ]

    minimum = content_div.find("strong", string="Minimum Requirements:")
    if minimum:
        ul = minimum.find_next("ul")
        if ul:
            job_data["minimum_requirements"] = [
                li.get_text(strip=True) for li in ul.find_all("li")
            ]

    disclaimer = content_div.find("strong", string="Disclaimer")
    if disclaimer:
        job_data["disclaimer"] = (
            disclaimer.find_parent("p")
            .get_text(" ", strip=True)
            .replace("Disclaimer", "")
        )

    return job_data