from tortoise import Tortoise
import os
from models import courses, steps, trainingmaterial

async def lifespan(_):
    await Tortoise.init(
        db_url=os.environ.get("DATABASE_URL"),
        modules={
            "models": [
                "models.user",
                "models.jobs",
                "models.courses",
                "models.steps",
                "models.trainingmaterial",
            ]
        },
    )
    await Tortoise.generate_schemas()
    yield
    await Tortoise.close_connections()
