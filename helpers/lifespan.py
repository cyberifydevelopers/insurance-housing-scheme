from tortoise import Tortoise
import os
from apscheduler.triggers.cron import CronTrigger
from apscheduler.schedulers.asyncio import AsyncIOScheduler
# from helpers.jobs import crsth_job_update, alacrity_job_update, alacrity_job_detail
from controllers.job_controller import sedgwick_scrape,alacrity_scrap,scrape_jobs

scheduler = AsyncIOScheduler()


async def scrape_jobs_task():
    print("🟡 Jobs update started...")
    try:
        await alacrity_scrap()
        await scrape_jobs()
        # await alacrity_job_update()
        await sedgwick_scrape()
        print("✅ Jobs updated successfully.")
    except Exception as e:
        print(f"❌ Error during job update: {e}")


async def lifespan(app):
    await Tortoise.init(
        db_url=os.environ.get("DATABASE_URL"),
        modules={
            "models": [
                "models.user",
                "models.jobs",
                "models.courses",
                "models.steps",
                "models.trainingmaterial",
                "models.user_registration",
            ]
        },
    )
    await Tortoise.generate_schemas()
    print("📦 Database initialized successfully.")

    scheduler.add_job(
        scrape_jobs_task,
        trigger=CronTrigger(hour="*/4", minute=0),
        id="update_jobs",
        replace_existing=True,
    )
    scheduler.start()
    print("✅ Scheduler started. Jobs will update every 2 minutes.")
    yield
    print("🛑 Shutting down FastAPI...")
    scheduler.shutdown()
    await Tortoise.close_connections()
    print("🔒 Database connections closed.")