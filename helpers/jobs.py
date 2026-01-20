from models.jobs import Job
from helpers.job_scraper import (
    job_scraper, # crsth job scrapper 
    description_scraper,
    alacrity_jobs,
    alacrity_job_detail,
    tacares_job_details,
)
from helpers.ai_filter_job import ai_job_filter
import asyncio
import json
from helpers.alacrity_job_filter import alacrity_job_filter
from helpers.logger_config import get_logger
from helpers.job_scraper import enrich_jobs_with_details
from controllers.job_controller import transform_job_for_frontend,find_new_jobs
import os 
from helpers.job_notification_email import JobNotificationEmailService
import logging
logger = get_logger(__name__)
logging.disable(logging.CRITICAL)

# async def crsth_job_update():
#     print("🟡 Starting CRSTH job update...")
#     job_record = await Job.filter(title="crsth").first()
#     jobs = await job_scraper()
#     filtered_jobs = await ai_job_filter(jobs) if jobs else []

#     if filtered_jobs:
#         descriptions = await asyncio.gather(
#             *(description_scraper(job["url"]) for job in filtered_jobs)
#         )
#         for job, full_description in zip(filtered_jobs, descriptions):
#             structured_description = " ".join(
#                 p.strip() for p in full_description.split("\n") if p.strip()
#             )
#             job["detail"] = structured_description

#         jobs_json = json.dumps(filtered_jobs, ensure_ascii=False, indent=4)

#         if job_record:
#             job_record.jobs = jobs_json
#             await job_record.save()
#         else:
#             await Job.create(title="crsth", jobs=jobs_json)

#         return {"message": "CRSTH jobs updated successfully."}

#     return {"message": "No filtered jobs found, nothing updated."}


async def crsth_job_update():
    # 1️⃣ Scrape + enrich
    logger.info("Starting CRSTH job scraping process.")
    jobs = await job_scraper()
    jobs = await enrich_jobs_with_details(jobs)

    # 2️⃣ AI filter
    filtered_jobs = await ai_job_filter(jobs) if jobs else []
    logger.info(f"CRSTH job scraping process done. Found {len(filtered_jobs)} jobs.")

    # 3️⃣ Format jobs for frontend
    formatted_jobs = []
    for job in filtered_jobs:
        formatted_jobs.append({
        "url": job.get("url"),
        "title": job.get("title"),  # 👈 REQUIRED for list view
        "description": job.get("description"),  # 👈 REQUIRED for list view
        "detail": json.dumps(transform_job_for_frontend(job),ensure_ascii=False)})


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


async def alacrity_job_update():
    job_record = await Job.filter(title="alacrity").first()
    jobs = await alacrity_jobs()
    ai_filtered_jobs = []

    if jobs:
        ai_filtered_jobs = await alacrity_job_filter(jobs)
        for job in ai_filtered_jobs:
            job["detail"] = await alacrity_job_detail(job["link"])

        jobs_json = json.dumps(ai_filtered_jobs, ensure_ascii=False, indent=4)

        if job_record:
            job_record.jobs = jobs_json
            await job_record.save()
        else:
            await Job.create(title="alacrity", jobs=jobs_json)

        return {"message": "Alacrity jobs updated successfully."}

    return {"message": "No filtered jobs found, nothing updated."}


async def tacares_job_update():
    job_record = await Job.filter(title="tacares").first()
    job_details = await tacares_job_details()

    if job_record:
        job_record.jobs = job_details
        await job_record.save()
    else:
        job_record = await Job.create(title="tacares", jobs=job_details)

    return {"job_details": job_details, "db_id": job_record.id}
