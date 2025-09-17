from models.jobs import Job
from helpers.job_scraper import (
    job_scraper,
    description_scraper,
    alacrity_jobs,
    alacrity_job_detail,
    tacares_job_details,
)
from helpers.ai_filter_job import ai_job_filter
import asyncio
import json
from helpers.alacrity_job_filter import alacrity_job_filter


async def crsth_job_update():
    job_record = await Job.filter(title="crsth").first()
    jobs = await job_scraper()
    filtered_jobs = await ai_job_filter(jobs) if jobs else []

    if filtered_jobs:
        descriptions = await asyncio.gather(
            *(description_scraper(job["url"]) for job in filtered_jobs)
        )
        for job, full_description in zip(filtered_jobs, descriptions):
            structured_description = " ".join(
                p.strip() for p in full_description.split("\n") if p.strip()
            )
            job["detail"] = structured_description

        jobs_json = json.dumps(filtered_jobs, ensure_ascii=False, indent=4)

        if job_record:
            job_record.jobs = jobs_json
            await job_record.save()
        else:
            await Job.create(title="crsth", jobs=jobs_json)

        return {"message": "CRSTH jobs updated successfully."}

    return {"message": "No filtered jobs found, nothing updated."}


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
