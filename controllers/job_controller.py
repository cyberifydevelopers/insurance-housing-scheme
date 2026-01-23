import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)  # if LangChain uses UserWarning
import asyncio
from fastapi import APIRouter
from helpers.ai_filter_job import ai_job_filter
from helpers.sedgwick_jobs import scrape_sedgwick_jobs
from helpers.job_scraper import (
    job_scraper,
    description_scraper,
    alacrity_jobs,
    alacrity_job_detail,
    tacares_job_details,
    enrich_jobs_with_details,
)
from helpers.alacrity_job_filter import alacrity_job_filter
from models.jobs import Job
from fastapi import APIRouter, HTTPException
import json
import httpx
import os
from helpers.find_jobs import find_crths_job, find_alacrity_job
from pydantic import BaseModel
from typing import List
from helpers.apply_jobs import alacrity_job_apply, crsth_job_apply
from helpers.job_notification_email import JobNotificationEmailService
import logging 
from helpers.logger_config import get_logger
logger = get_logger(__name__)

logging.disable(logging.CRITICAL)


router = APIRouter(prefix="/api/job")


class LinkRequest(BaseModel):
    data: List[str]  # array of links


def find_new_jobs(old_jobs, new_jobs, key="url"):
    old_urls = set()
    
    if old_jobs:
        logger.info(f"Finding new jobs from {len(old_jobs)} old jobs and {len(new_jobs)} new jobs.")
        for job in old_jobs:
            if isinstance(job, dict) and job.get(key):
                old_urls.add(job[key])

    return [job for job in new_jobs if job.get(key) and job.get(key) not in old_urls]



def transform_job_for_frontend(job: dict) -> dict:
    logger.info(f"Transforming job for frontend: {job.get('title')}")
    return {
        "job_title": job.get("title"),
        "job_details": {
            "job_location": job.get("location"),
            "remote_type": "Hybrid" if "Hybrid" in job.get("job_type", "") else "Onsite",
            "position_type": job.get("job_type"),
            "salary_range": job.get("salary"),
            "job_category": "Corporate Housing"
        },
        "job_description": {
            "description": job.get("description"),
            "responsibilities": [
                line.strip()
                for line in job.get("full_description", [])
                if line and len(line) < 200
            ]
        },
        "qualifications": [
            q.strip("• ").strip()
            for block in job.get("qualifications", [])
            for q in block.split("\n")
            if q.strip()
        ]
    }




# @router.get("/crsth-scrape")
# async def scrape_jobs():
#     jobs = await job_scraper()
#     jobs =await enrich_jobs_with_details(jobs)

#     filtered_jobs = await ai_job_filter(jobs) if jobs else []
#     # if filtered_jobs:
#     #     descriptions = await asyncio.gather(
#     #         *(description_scraper(job["url"]) for job in filtered_jobs)
#     #     )
#     #     for job, full_description in zip(filtered_jobs, descriptions):
#     #         structured_description = " ".join(
#     #             p.strip() for p in full_description.split("\n") if p.strip()
#     #         )
#     #         job["detail"] = structured_description
#     #     for job in filtered_jobs:
#     #         urls = await find_crths_job(job)
#     #         job["other_sites"] = urls
#     jobs_json = json.dumps(filtered_jobs, ensure_ascii=False, indent=4)
#     formatted_jobs = []

#     for job in jobs_json:
#         formatted_jobs.append({
#             "url": job.get("url"),
#             "detail": json.dumps(
#                 transform_job_for_frontend(job),
#                 ensure_ascii=False
#             )
#         })

#     # jobs_json = json.dumps(jobs, ensure_ascii=False, indent=4)
#     existing_job = await Job.filter(title="crsth").first()
#     if existing_job:
#         existing_job.jobs = jobs_json
#         await existing_job.save()
#     # else:
#     #     await Job.create(title="crsth", jobs=jobs_json)
#     # return {"message": "CRSTH jobs scraping done", "jobs": filtered_jobs}
#     email_service = JobNotificationEmailService()


#     notify_email = os.getenv("JOB_NOTIFICATION_EMAIL")  # e.g. admin@company.com

#     existing_job = await Job.filter(title="crsth").first()

#     old_jobs = []
#     if existing_job and existing_job.jobs:
#         old_jobs = json.loads(existing_job.jobs)

#     new_jobs = find_new_jobs(old_jobs, jobs, key="url")

#     # Send email ONLY if new jobs found
#     if new_jobs:
#         email_service.send_new_jobs_email(to_email=notify_email, jobs=new_jobs)

#     # jobs_json = json.dumps(filtered_jobs, ensure_ascii=False, indent=4)
#     jobs_json = json.dumps(jobs, ensure_ascii=False, indent=4)
#     if existing_job:
#         existing_job.jobs = jobs_json
#         await existing_job.save()
#     else:
#         await Job.create(title="crsth", jobs=jobs_json)
#     return {
#     "message": "CRSTH jobs scraping done",
#     "new_jobs_found": len(new_jobs),
#     "jobs": jobs
# }




@router.get("/crsth-scrape")
async def scrape_jobs():
    # 1️⃣ Scrape + enrich
    logger.info("Starting CRSTH job scraping process.")
    
    try:
        jobs = await job_scraper()
        jobs = await enrich_jobs_with_details(jobs)
    except Exception as e:
        logger.error(f"Scraping failed: {str(e)}")
        return {
            "message": "CRSTH jobs scraping failed - existing data preserved",
            "error": str(e),
            "new_jobs_found": 0
        }

    # 2️⃣ AI filter
    filtered_jobs = await ai_job_filter(jobs) if jobs else []
    logger.info(f"CRSTH job scraping process done. Found {len(filtered_jobs)} jobs.")

    # 🛡️ CRITICAL: Don't update DB if scraping returned no results
    if not filtered_jobs:
        logger.warning("No jobs found from scraping. Preserving existing database records.")
        return {
            "message": "CRSTH scraping returned 0 jobs - existing data preserved",
            "new_jobs_found": 0,
            "jobs": []
        }

    # 3️⃣ Format jobs for frontend
    formatted_jobs = []
    for job in filtered_jobs:
        formatted_jobs.append({
            "url": job.get("url"),
            "title": job.get("title"),
            "description": job.get("description"),
            "detail": json.dumps(transform_job_for_frontend(job), ensure_ascii=False)
        })

    # 4️⃣ Load existing jobs (for email diff)
    existing_job = await Job.filter(title="crsth").first()

    # Handle both string and list types
    if existing_job and existing_job.jobs:
        if isinstance(existing_job.jobs, str):
            old_jobs = json.loads(existing_job.jobs)
        else:
            old_jobs = existing_job.jobs  # Already a list
    else:
        old_jobs = []

    # 5️⃣ Find newly added jobs
    new_jobs = find_new_jobs(old_jobs, formatted_jobs, key="url")
    logger.info(f"Found {len(new_jobs)} new CRSTH jobs.")
    
    # 6️⃣ Send email if new jobs found
    if new_jobs:
        email_service = JobNotificationEmailService()
        notify_email = os.getenv("JOB_NOTIFICATION_EMAIL")
        email_service.send_new_jobs_email(
            to_email=notify_email,
            jobs=new_jobs
        )

    # 7️⃣ Save FRONTEND-COMPATIBLE jobs to DB
    jobs_json = json.dumps(formatted_jobs, ensure_ascii=False, indent=4)

    if existing_job:
        existing_job.jobs = jobs_json
        await existing_job.save()
    else:
        await Job.create(title="crsth", jobs=jobs_json)

    # 8️⃣ API response
    return {
        "message": "CRSTH jobs scraping done",
        "new_jobs_found": len(new_jobs),
        "jobs": formatted_jobs
    }



# @router.get("/alacrity-scrape")
# async def alacrity_scrap():
#     jobs = await alacrity_jobs()
#     ai_filtered_jobs = []
#     if jobs:
#         ai_filtered_jobs = await alacrity_job_filter(jobs)
#         print("Ai filtered jobs", ai_filtered_jobs)
#         for job in ai_filtered_jobs:
#             job["detail"] = await alacrity_job_detail(job["link"])
#             print("job detail", job["detail"])

#     jobs_json = json.dumps(ai_filtered_jobs, ensure_ascii=False, indent=4)
#     # print("jobs_json", jobs_json)
#     # is_job_exists = await Job.filter(title="alacrity").first()
#     # if is_job_exists:
#     #     is_job_exists.jobs = jobs_json
#     #     await is_job_exists.save()
#     # else:
#     #     await Job.create(title="alacrity", jobs=jobs_json)
#     # return {
#     #     "message": "Alacrity jobs scraping done",
#     #     "jobs": ai_filtered_jobs,
#     # }
#     email_service = JobNotificationEmailService()
#     notify_email = os.getenv("JOB_NOTIFICATION_EMAIL")

#     existing_job = await Job.filter(title="alacrity").first()

#     # old_jobs = []
#     # if existing_job and existing_job.jobs:
#     #     old_jobs = json.loads(existing_job.jobs)
#     old_jobs = []
#     if existing_job and existing_job.jobs:
#         if isinstance(existing_job.jobs, str):
#             old_jobs = json.loads(existing_job.jobs)
#         elif isinstance(existing_job.jobs, list):
#             old_jobs = existing_job.jobs


#     old_links = {job.get("link") for job in old_jobs if isinstance(job, dict)}
#     new_jobs = find_new_jobs(old_jobs, ai_filtered_jobs, key="link")

#     # Send email only if new jobs exist
#     if new_jobs and notify_email:
#         email_service.send_new_jobs_email(
#             to_email=notify_email,
#             jobs=new_jobs
#         )

#     # Save updated jobs
#     if existing_job:
#         existing_job.jobs = jobs_json
#         await existing_job.save()
#     else:
#         await Job.create(title="alacrity", jobs=jobs_json)

#     return {
#         "message": "Alacrity jobs scraping done",
#         "new_jobs_found": len(new_jobs),
#         "jobs": ai_filtered_jobs
#     }


@router.get("/alacrity-scrape")
async def alacrity_scrap():
    """Scrape Alacrity jobs with filtering and data protection"""
    
    # 1️⃣ Try to scrape jobs
    try:
        jobs = await alacrity_jobs()
    except Exception as e:
        logger.error(f"Alacrity scraping failed: {str(e)}")
        return {
            "message": "Alacrity jobs scraping failed - existing data preserved",
            "error": str(e),
            "new_jobs_found": 0
        }
    
    # 2️⃣ Guard against empty results
    if not jobs:
        logger.warning("No Housing Account Manager jobs found. Preserving existing database records.")
        return {
            "message": "Alacrity scraping returned 0 matching jobs - existing data preserved",
            "new_jobs_found": 0,
            "jobs": []
        }
    
    # 3️⃣ AI filter
    ai_filtered_jobs = []
    try:
        ai_filtered_jobs = await alacrity_job_filter(jobs)
        logger.info(f"AI filtered jobs: {len(ai_filtered_jobs)}")
    except Exception as e:
        logger.error(f"AI filtering failed: {str(e)}")
        # Use unfiltered jobs if AI filter fails
        ai_filtered_jobs = jobs
    
    # 4️⃣ Guard against AI filter removing all jobs
    if not ai_filtered_jobs:
        logger.warning("AI filter removed all jobs. Preserving existing database records.")
        return {
            "message": "AI filtering returned 0 jobs - existing data preserved",
            "new_jobs_found": 0,
            "jobs": []
        }
    
    # 5️⃣ Enrich with job details
    for job in ai_filtered_jobs:
        try:
            job["detail"] = await alacrity_job_detail(job["link"])
            logger.info(f"Enriched job detail for: {job['title']}")
        except Exception as e:
            logger.error(f"Failed to get details for {job['title']}: {str(e)}")
            job["detail"] = None  # Don't fail entire scrape if one detail fails

    # 6️⃣ Load existing jobs (for email diff)
    existing_job = await Job.filter(title="alacrity").first()

    old_jobs = []
    if existing_job and existing_job.jobs:
        if isinstance(existing_job.jobs, str):
            old_jobs = json.loads(existing_job.jobs)
        elif isinstance(existing_job.jobs, list):
            old_jobs = existing_job.jobs

    # 7️⃣ Find new jobs and send email
    new_jobs = find_new_jobs(old_jobs, ai_filtered_jobs, key="link")
    logger.info(f"Found {len(new_jobs)} new Alacrity jobs")

    if new_jobs:
        email_service = JobNotificationEmailService()
        notify_email = os.getenv("JOB_NOTIFICATION_EMAIL")
        if notify_email:
            try:
                email_service.send_new_jobs_email(
                    to_email=notify_email,
                    jobs=new_jobs
                )
            except Exception as e:
                logger.error(f"Failed to send email notification: {str(e)}")

    # 8️⃣ Save to database
    jobs_json = json.dumps(ai_filtered_jobs, ensure_ascii=False, indent=4)
    
    if existing_job:
        existing_job.jobs = jobs_json
        await existing_job.save()
    else:
        await Job.create(title="alacrity", jobs=jobs_json)

    # 9️⃣ Return response
    return {
        "message": "Alacrity jobs scraping done",
        "new_jobs_found": len(new_jobs),
        "total_jobs": len(ai_filtered_jobs),
        "jobs": ai_filtered_jobs
    }


# @router.get("/tacares-scrape")
# async def tacares_scrape():
#     job_details = await tacares_job_details()
#     job = await Job.create(title="tacares", jobs=job_details)
#     return {"job_details": job_details, "db_id": job.id}



@router.get("/sedgwick-scrape")
async def sedgwick_scrape():
    """
    Scrape Sedgwick job listings for Housing Coordinator positions
    Returns job details and sends email notification for new jobs
    """
    # Import here to avoid circular imports
    # Adjust import based on your project structure
    # from services.email_service import JobNotificationEmailService  # Adjust import
    
    # Scrape jobs
    job_details_list = scrape_sedgwick_jobs()
    
    if not job_details_list:
        return {
            "message": "No jobs found or scraping failed",
            "success": False,
            "jobs_found": 0,
            "new_jobs": []
        }
    
    # Email service setup
    email_service = JobNotificationEmailService()
    notify_email = os.getenv("JOB_NOTIFICATION_EMAIL")
    
    # Get existing jobs from database
    existing_job = await Job.filter(title="sedgwick").first()
    
    new_jobs = []
    existing_job_ids = set()
    
    # Parse existing jobs
    if existing_job and existing_job.jobs:
        if isinstance(existing_job.jobs, str):
            old_jobs = json.loads(existing_job.jobs)
        elif isinstance(existing_job.jobs, dict):
            old_jobs = existing_job.jobs
        elif isinstance(existing_job.jobs, list):
            old_jobs = existing_job.jobs
        else:
            old_jobs = []
        
        # Handle both single job dict and list of jobs
        if isinstance(old_jobs, dict):
            old_jobs = [old_jobs]
        
        # Get existing job IDs
        for job in old_jobs:
            if isinstance(job, dict) and job.get('job_id'):
                existing_job_ids.add(job['job_id'])
    
    # Check for new jobs
    for job in job_details_list:
        if job.get('job_id') not in existing_job_ids:
            new_jobs.append(job)
    
    # Send email ONLY if there are new jobs
    if new_jobs and notify_email:
        try:
            email_service.send_new_jobs_email(
                to_email=notify_email,
                jobs=new_jobs
            )
            pass  # Uncomment above when email service is ready
        except Exception as e:
            pass  # Log error but don't fail the request
    
    # Save/update jobs in database
    jobs_json = json.dumps(job_details_list, ensure_ascii=False, indent=2)
    
    if existing_job:
        existing_job.jobs = jobs_json
        await existing_job.save()
        db_id = existing_job.id
    else:
        new_record = await Job.create(title="sedgwick", jobs=jobs_json)
        db_id = new_record.id
    
    return {
        "message": "Sedgwick job scraping completed successfully",
        "success": True,
        "jobs_found": len(job_details_list),
        "new_jobs_count": len(new_jobs),
        "new_jobs": new_jobs,
        "all_jobs": job_details_list,
        "db_id": db_id,
    }
# async def tacares_scrape():
#     job_details = await tacares_job_details()

#     email_service = JobNotificationEmailService()
#     notify_email = os.getenv("JOB_NOTIFICATION_EMAIL")

#     existing_job = await Job.filter(title="tacares").first()

#     is_new_job = True

#     if existing_job and existing_job.jobs:
#         if isinstance(existing_job.jobs, str):
#             old_job = json.loads(existing_job.jobs)
#         elif isinstance(existing_job.jobs, dict):
#             old_job = existing_job.jobs
#         else:
#             old_job = None

#         if (
#             isinstance(old_job, dict)
#             and old_job.get("url") == job_details.get("url")
#         ):
#             is_new_job = False


#     # Send email ONLY if job is new
#     if is_new_job and notify_email:
#         email_service.send_new_jobs_email(
#             to_email=notify_email,
#             jobs=[job_details]  # wrap in list to reuse email template
#         )

#     # Save / update job
#     job_json = json.dumps(job_details, ensure_ascii=False, indent=4)

#     if existing_job:
#         existing_job.jobs = job_json
#         await existing_job.save()
#     else:
#         existing_job = await Job.create(title="tacares", jobs=job_json)

#     return {
#         "message": "Tacares job scraping done",
#         "new_job_found": is_new_job,
#         "job_details": job_details,
#         "db_id": existing_job.id,
#     }


@router.post("/apply-on-alacrity")
async def apply_on_alacrity(payload: LinkRequest):
    links = payload.data
    # for link in links:
    res = alacrity_job_apply(links[5])
    print(res)
    return {"received": links, "count": len(links)}


@router.post("/apply-on-crsth")
async def apply_on_crsth(payload: LinkRequest):
    links = payload.data
    res = crsth_job_apply(links[0])
    print(res)
    return {"received": links, "count": len(links)}


# @router.get("/indeed-jobs")
# async def get_jobs(position: str = "Housing Specialist", page: int = 1):
#     url = f"https://indeed12.p.rapidapi.com/jobs/search?query={position}&fromage=7&jt=permanent&page={page}"

#     headers = {
#         "X-RapidAPI-Key": os.environ.get("INDEED_API_KEY"),
#         "X-RapidAPI-Host": "indeed12.p.rapidapi.com",
#     }

#     async with httpx.AsyncClient(timeout=30.0) as client:
#         response = await client.get(url, headers=headers)
#         print(response.status_code, response.text)

#         try:
#             data = response.json()
#             hits = data.get("hits", [])
#             if not hits:
#                 return {
#                     "message": "No jobs found, try adjusting position, location, or filters.",
#                     "jobs": [],
#                 }
#             return {"jobs": hits}
#         except ValueError:
#             return {"error": "Invalid response from API", "content": response.text}


@router.get("/get-crsth-urls")
async def get_crsth_urls():
    job = await Job.filter(title="crsth").first()
    urls = await find_crths_job(job.jobs)
    return {"data": urls}


@router.get("/get-alacrity-urls")
async def get_alacrity_urls():
    job = await Job.filter(title="alacrity").first()
    urls = await find_alacrity_job(job.jobs)
    return {"data": urls}


@router.delete("/delete/{id}")
async def delete_job(id: int):
    job = await Job.get_or_none(id=id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    await job.delete()
    return {"message": "Job deleted successfully"}


async def fetch_jobs(position: str, page: int = 1):
    url = f"https://indeed12.p.rapidapi.com/jobs/search?query={position}&fromage=7&jt=permanent&page={page}"
    headers = {
        "X-RapidAPI-Key": os.environ.get("INDEED_API_KEY"),
        "X-RapidAPI-Host": "indeed12.p.rapidapi.com",
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        return response.json()


# @router.get("/indeed-jobs")
# async def get_all_jobs(position: str = "Housing Scheme"):
#     all_jobs = []
#     page = 1
#     while True:
#         try:
#             data = await fetch_jobs(position, page)
#             hits = data.get("hits", [])
#             if not hits:
#                 break
#             all_jobs.extend(hits)
#             page += 1
#         except Exception as e:
#             print(f"Error on page {page}: {e}")
#             break
#     is_job_exists = await Job.filter(title="indeed").first()
#     if is_job_exists:
#         is_job_exists.jobs = all_jobs
#         await is_job_exists.save()
#     else:
#         await Job.create(
#             title="indeed",
#             jobs={"items": all_jobs},
#         )
#     return {"total_jobs": len(all_jobs), "jobs": all_jobs}

@router.get("/indeed-jobs")
async def get_all_jobs(position: str = "Housing Scheme"):
    all_jobs = []
    page = 1

    while True:
        try:
            data = await fetch_jobs(position, page)
            print(f"Indeed API response page {page}:", data)
            hits = data.get("hits", [])
            if not hits:
                break
            all_jobs.extend(hits)
            page += 1
        except Exception as e:
            print(f"Error on page {page}: {e}")
            break

    email_service = JobNotificationEmailService()
    notify_email = os.getenv("JOB_NOTIFICATION_EMAIL")

    existing_job = await Job.filter(title="indeed").first()

    old_jobs = []
    if existing_job and existing_job.jobs:
        if isinstance(existing_job.jobs, str):
            old_jobs = json.loads(existing_job.jobs).get("items", [])
        elif isinstance(existing_job.jobs, dict):
            old_jobs = existing_job.jobs.get("items", [])

    # 🔍 Find only NEW jobs (by Indeed job ID)
    new_jobs = find_new_jobs(old_jobs, all_jobs, key="id")

    # ✉️ Send email ONLY if new jobs exist
    if new_jobs and notify_email:
        email_service.send_new_jobs_email(
            to_email=notify_email,
            jobs=new_jobs
        )

    # 💾 Save updated jobs
    jobs_payload = {"items": all_jobs}

    if existing_job:
        existing_job.jobs = json.dumps(jobs_payload, ensure_ascii=False, indent=4)
        await existing_job.save()
    else:
        await Job.create(
            title="indeed",
            jobs=json.dumps(jobs_payload, ensure_ascii=False, indent=4),
        )

    return {
        "total_jobs": len(all_jobs),
        "new_jobs_found": len(new_jobs),
        "jobs": all_jobs,
    }


@router.get("/get")
async def jobs():
    jobs = await Job.all()
    # print("--------------length of job--------------", len(jobs))
    if not jobs:
        raise HTTPException(404, "Jobs not found.")
    return {"jobs": jobs}
