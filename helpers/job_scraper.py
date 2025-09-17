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


async def job_scraper():
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=chrome_options
    )
    try:
        url = "https://crsth.com/careers/"
        driver.get(url)
        wait = WebDriverWait(driver, 30)
        iframe = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "iframe")))
        driver.switch_to.frame(iframe)
        jobs = []
        seen_urls = set()
        select_el = wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "select.countDropdown.browser-default")
            )
        )
        select = Select(select_el)
        option_values = [opt.get_attribute("value") for opt in select.options]
        for value in option_values:
            select_el = wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "select.countDropdown.browser-default")
                )
            )
            select = Select(select_el)
            select.select_by_value(value)
            time.sleep(2)
            parents = wait.until(
                EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, "li.jobInfo.JobListing")
                )
            )
            for parent in parents:
                try:
                    title_el = parent.find_element(
                        By.CSS_SELECTOR, "span.jobInfoLine.jobTitle"
                    )
                    url_el = parent.find_element(
                        By.CSS_SELECTOR, "a.JobListing__container"
                    )
                    subtitle_el = parent.find_element(
                        By.CSS_SELECTOR,
                        "span.jobInfoLine.jobLocation.JobListing__subTitle",
                    )
                    desc_el = parent.find_element(
                        By.CSS_SELECTOR, "span.jobInfoLine.jobDescription"
                    )
                    job_url = url_el.get_attribute("href")
                    if job_url not in seen_urls:
                        job = {
                            "title": title_el.text.strip(),
                            "url": job_url,
                            "subtitle": subtitle_el.text.strip(),
                            "description": desc_el.text.strip(),
                        }
                        jobs.append(job)
                        seen_urls.add(job_url)
                except Exception as e:
                    print("Error parsing job:", e)
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
    url = "https://www.tacares.com/housing-support-specialist/"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    content_div = soup.find("div", class_="bf-cpc-content")
    job_data = {}
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
