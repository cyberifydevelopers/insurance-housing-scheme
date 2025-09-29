from fastapi import APIRouter, HTTPException
from models.courses import Course
from pydantic import BaseModel
from models.steps import Step
from models.trainingmaterial import TrainingMaterial
from helpers.files import delete_file

router = APIRouter(prefix="/api/steps", tags=["Steps"])


class CreateSteps(BaseModel):
    id: int = 0
    title: str
    courseId: int


@router.post("/create")
async def create_or_update_steps(data: CreateSteps):
    course = await Course.get_or_none(id=data.courseId)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    if data.id == 0:
        step = await Step.create(
            course=course,
            title=data.title,
        )
        return {"message": "Step created successfully", "step_id": step.id}
    else:
        existing_step = await Step.get_or_none(course_id=data.courseId, id=data.id)
        if not existing_step:
            raise HTTPException(status_code=404, detail="Step not found")
        existing_step.title = data.title
        await existing_step.save()
        return {
            "message": "Step updated successfully",
            "step_id": existing_step.id,
        }


@router.get("/get/{course_id}")
async def get_steps(course_id: int):
    steps = await Step.filter(course_id=course_id)
    result = []
    for step in steps:
        lessons_count = await TrainingMaterial.filter(
            course_id=course_id, step_id=step.id
        ).count()
        result.append(
            {
                "id": step.id,
                "title": step.title,
                "lessons": lessons_count,
            }
        )
    return {"steps": result}


@router.delete("/delete/{id}")
async def delete_step(id: int):
    step = await Step.get_or_none(id=id)
    if not step:
        raise HTTPException(status_code=404, detail="Step not found")
    lessons = await TrainingMaterial.filter(step=step).all()
    for lesson in lessons:
        if lesson.key:
            await delete_file(lesson.key)
    await TrainingMaterial.filter(step=step).delete()
    await step.delete()
    return {"message": "Step and its lessons deleted successfully"}
