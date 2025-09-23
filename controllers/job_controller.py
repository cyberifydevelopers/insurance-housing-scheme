import asyncio
from fastapi import APIRouter
from helpers.ai_filter_job import ai_job_filter
from helpers.job_scraper import (
    job_scraper,
    description_scraper,
    alacrity_jobs,
    alacrity_job_detail,
    tacares_job_details,
)
from helpers.alacrity_job_filter import alacrity_job_filter
from models.jobs import Job
from fastapi import APIRouter, HTTPException
import json
import httpx
import os

router = APIRouter(prefix="/api/job")


@router.get("/crsth-scrape")
async def scrape_jobs():
    # is_job_exist = await Job.filter(title="crsth").first()
    # if is_job_exist:
    #     raise HTTPException(400, "CRSTH already exists.")
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
    await Job.create(
        title="crsth",
        jobs=jobs_json,
    )
    return {"message": "CRSTH jobs scraping done", "jobs": filtered_jobs}


@router.get("/alacrity-scrape")
async def alacrity_scrap():
    jobs = await alacrity_jobs()
    ai_filtered_jobs = []
    if jobs:
        ai_filtered_jobs = await alacrity_job_filter(jobs)
        for job in ai_filtered_jobs:
            job["detail"] = await alacrity_job_detail(job["link"])
    jobs_json = json.dumps(ai_filtered_jobs, ensure_ascii=False, indent=4)
    await Job.create(
        title="alacrity",
        jobs=jobs_json,
    )
    return {
        "message": "Alacrity jobs scraping done",
    }


@router.get("/tacares-scrape")
async def tacares_scrape():
    job_details = await tacares_job_details()
    job = await Job.create(title="tacares", jobs=job_details)
    return {"job_details": job_details, "db_id": job.id}


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


@router.get("/indeed-jobs")
async def get_all_jobs(position: str = "Housing Scheme"):
    all_jobs = []
    page = 1
    while True:
        try:
            data = await fetch_jobs(position, page)
            hits = data.get("hits", [])
            if not hits:
                break
            all_jobs.extend(hits)
            page += 1
        except Exception as e:
            print(f"Error on page {page}: {e}")
            break
    await Job.create(
        title="indeed",
        jobs=all_jobs,
    )
    return {"total_jobs": len(all_jobs), "jobs": all_jobs}


@router.get("/get")
async def jobs():
    jobs = await Job.all()
    if not jobs:
        raise HTTPException(404, "Jobs not found.")
    return {"jobs": jobs}
