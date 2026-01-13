import os
import json
from tavily import TavilyClient

crsth_tavily = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))
alacrity_tavily = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))


async def find_crths_job(job: dict):
    try:
        detail = json.loads(job.get("detail", "{}"))
        title = detail.get("job_title") or job.get("title", "")
        location = detail.get("job_details", {}).get("job_location", "")
        query = f"{title} {location} site:indeed.com OR site:linkedin.com OR site:glassdoor.com"
        tavily_results = crsth_tavily.search(query)
        structured = []
        for r in tavily_results.get("results", []):
            structured.append(
                {
                    "title": r.get("title", title),
                    "description": r.get("content", ""),
                    "url": r.get("url", ""),
                }
            )
        return structured
    except Exception as e:
        return [{"error": str(e)}]


async def find_alacrity_job(job: dict):
    title = job.get("title", "")
    company = None
    location = job.get("location", "")

    try:
        detail = json.loads(job.get("detail", "{}"))
        if "company" in detail:
            company = detail["company"]
        if "job_details" in detail and "job_location" in detail["job_details"]:
            location = detail["job_details"]["job_location"]
    except Exception:
        pass
    parts = [title]
    if company:
        parts.append(company)
    if location:
        parts.append(location)

    query = (
        " ".join(parts) + " site:indeed.com OR site:linkedin.com OR site:glassdoor.com"
    )
    try:
        tavily_response = alacrity_tavily.search(
            query=query,
        )
        results = tavily_response.get("results", [])
        jobs_with_details = []
        for r in results:
            jobs_with_details.append(
                {
                    "title": r.get("title", ""),
                    "description": r.get("content", ""),
                    "url": r.get("url", ""),
                }
            )
        return jobs_with_details
    except Exception as e:
        print("Search failed:", e)
        return []
