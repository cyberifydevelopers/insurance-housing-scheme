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
from helpers.find_jobs import find_crths_job, find_alacrity_job
from pydantic import BaseModel
from typing import List
from helpers.apply_jobs import alacrity_job_apply, crsth_job_apply

router = APIRouter(prefix="/api/job")


class LinkRequest(BaseModel):
    data: List[str]  # array of links


@router.get("/crsth-scrape")
async def scrape_jobs():
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
        for job in filtered_jobs:
            urls = await find_crths_job(job)
            job["other_sites"] = urls
    jobs_json = json.dumps(filtered_jobs, ensure_ascii=False, indent=4)
    existing_job = await Job.filter(title="crsth").first()
    if existing_job:
        existing_job.jobs = jobs_json
        await existing_job.save()
    else:
        await Job.create(title="crsth", jobs=jobs_json)
    return {"message": "CRSTH jobs scraping done", "jobs": filtered_jobs}


@router.get("/alacrity-scrape")
async def alacrity_scrap():
    jobs = await alacrity_jobs()
    ai_filtered_jobs = []
    if jobs:
        ai_filtered_jobs = await alacrity_job_filter(jobs)
        print("Ai filtered jobs", ai_filtered_jobs)
        for job in ai_filtered_jobs:
            job["detail"] = await alacrity_job_detail(job["link"])
            print("job detail", job["detail"])

    jobs_json = json.dumps(ai_filtered_jobs, ensure_ascii=False, indent=4)
    print("jobs_json", jobs_json)
    is_job_exists = await Job.filter(title="alacrity").first()
    if is_job_exists:
        is_job_exists.jobs = jobs_json
        await is_job_exists.save()
    else:
        await Job.create(title="alacrity", jobs=jobs_json)
    return {
        "message": "Alacrity jobs scraping done",
        "jobs": ai_filtered_jobs,
    }


@router.get("/tacares-scrape")
async def tacares_scrape():
    job_details = await tacares_job_details()
    job = await Job.create(title="tacares", jobs=job_details)
    return {"job_details": job_details, "db_id": job.id}


@router.post("/apply-on-alacrity")
async def apply_on_alacrity(payload: LinkRequest):
    links = payload.data
    # for link in links:
    res = alacrity_job_apply(links[5])
    print(res)
    return {"received": links, "count": len(links)}


@router.post("/apply-on-crsth")
async def apply_on_alacrity(payload: LinkRequest):
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
    is_job_exists = await Job.filter(title="indeed").first()
    if is_job_exists:
        is_job_exists.jobs = all_jobs
        await is_job_exists.save()
    else:
        await Job.create(
            title="indeed",
            jobs={"items": all_jobs},
        )
    return {"total_jobs": len(all_jobs), "jobs": all_jobs}


@router.get("/get")
async def jobs():
    jobs = await Job.all()
    if not jobs:
        raise HTTPException(404, "Jobs not found.")
    return {"jobs": jobs}
