# routers/course.py
from fastapi import APIRouter, HTTPException
from models.courses import Course
from pydantic import BaseModel
from models.steps import Step
from models.trainingmaterial import TrainingMaterial
from helpers.files import delete_file

router = APIRouter(prefix="/api/course", tags=["Course"])


class CreateCourse(BaseModel):
    id: int = 0
    title: str
    description: str


@router.post("/create")
async def create_or_update_course(data: CreateCourse):
    if data.id == 0:
        course = await Course.create(title=data.title, description=data.description)
        return {"message": "Course created successfully", "course_id": course.id}
    else:
        existing_course = await Course.get_or_none(id=data.id)
        if not existing_course:
            raise HTTPException(status_code=404, detail="Course not found")
        existing_course.title = data.title
        existing_course.description = data.description
        await existing_course.save()
        return {
            "message": "Course updated successfully",
            "course_id": existing_course.id,
        }


@router.get("/get")
async def get_courses():
    courses = await Course.all()
    result = []
    for course in courses:
        steps_count = await Step.filter(course_id=course.id).count()
        result.append(
            {
                "id": course.id,
                "title": course.title,
                "description": course.description or "",
                "steps_count": steps_count,
            }
        )
    return {"courses": result}


@router.delete("/delete/{id}")
async def delete_course(id: int):
    course = await Course.get_or_none(id=id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    steps = await Step.filter(course=course).all()
    for step in steps:
        lessons = await TrainingMaterial.filter(step=step).all()
        for lesson in lessons:
            if lesson.key:
                await delete_file(lesson.key)
        await TrainingMaterial.filter(step=step).delete()
        await step.delete()
    await course.delete()
    return {"message": "Course deleted successfully"}
