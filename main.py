from dotenv import load_dotenv
load_dotenv()
from controllers import traning_material_controller
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from controllers import job_controller, auth_controller,course_controller,steps_controller
from helpers.lifespan import lifespan

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_controller.router, tags=["Users"])
app.include_router(job_controller.router, tags=["Jobs"])
app.include_router(course_controller.router, tags=["Course"])
app.include_router(steps_controller.router, tags=["Steps"])
app.include_router(traning_material_controller.router, tags=["Traning Material"])


# async def job_update_cron_job():
#     print("Jobs updation start")
#     await crsth_job_update()
#     await alacrity_job_update()
#     await tacares_job_update()
#     print("Jobs updated successfully")

# def schedule_job():
#     asyncio.create_task(job_update_cron_job()) 

# scheduler = AsyncIOScheduler()
# scheduler.add_job(
#     schedule_job,
#     trigger="cron",
#     hour=0,
#     minute=0,
# )
# scheduler.start()


@app.get("/")
def say_hello():
    return {"message": "Welcome from server!"}


# @app.on_event("shutdown")
# def shutdown_event():
#     scheduler.shutdown()
