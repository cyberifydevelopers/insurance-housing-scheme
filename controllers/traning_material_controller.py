from pydantic import BaseModel
from fastapi import APIRouter, File, Form, UploadFile, HTTPException
import uuid
import os
import aioboto3
from helpers.files import delete_file
from models.trainingmaterial import TrainingMaterial
from models.courses import Course
from models.steps import Step

router = APIRouter(prefix="/api/training-material")


class CreateTraningMaterial(BaseModel):
    id: int
    title: str
    file_url: str
    stepId: int
    courseId: int
    type: str
    key: str

@router.post("/save")
async def save_traning_material(data: CreateTraningMaterial):
    course = await Course.get_or_none(id=data.courseId)
    step = await Step.get_or_none(id=data.stepId)
    if not course or not step:
        raise HTTPException(status_code=404, detail="Course or Step not found")
    if data.id == 0:
        new_material = await TrainingMaterial.create(
            title=data.title,
            file_url=data.file_url,
            step=step,
            course=course,
            type=data.type,
            key=data.key,
        )
        return {
            "message": "Training material created successfully",
            "material_id": new_material.id,
        }
    else:
        existing_material = await TrainingMaterial.get_or_none(id=data.id)
        if not existing_material:
            raise HTTPException(status_code=404, detail="Training material not found")
        if existing_material.key != data.key:
            await delete_file(existing_material.key)
        existing_material.title = data.title
        existing_material.file_url = data.file_url
        existing_material.step = step
        existing_material.course = course
        existing_material.type = data.type
        existing_material.key = data.key
        await existing_material.save()
        return {
            "message": "Training material updated successfully",
            "material_id": existing_material.id,
        }

@router.get("/get/{course_id}/{step_id}")
async def get_traning_material(course_id: int, step_id: int):
    materials = await TrainingMaterial.filter(course_id=course_id, step_id=step_id).all()
    return {"materials": materials}


@router.post("/upload-file")
async def upload_file(file: UploadFile = File(...), folder_name: str = Form(...)):
    try:
        ext = os.path.splitext(file.filename)[1]
        unique_name = f"{uuid.uuid4().hex}{ext}"
        s3_key = f"{folder_name}/{unique_name}"
        bucket_name = os.environ.get("BUCKET_NAME")
        region = os.environ.get("AWS_REGION")

        if not bucket_name or not region:
            raise HTTPException(status_code=500, detail="S3 config missing")

        session = aioboto3.Session()
        async with session.client(
            "s3",
            aws_access_key_id=os.environ.get("AWS_ACCESS_KEY"),
            aws_secret_access_key=os.environ.get("AWS_SECRET_KEY"),
            region_name=region,
        ) as s3_client:
            await s3_client.upload_fileobj(
                file.file,
                bucket_name,
                s3_key,
                ExtraArgs={"ContentType": file.content_type or "application/octet-stream"},
            )

        file_url = f"https://{bucket_name}.s3.{region}.amazonaws.com/{s3_key}"
        return {
            "success": True,
            "message": f"File '{file.filename}' uploaded successfully as '{unique_name}'.",
            "file_url": file_url,
            "key": s3_key,
            "folder": folder_name,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))    


@router.delete("/delete/{id}")
async def delete_traning_material(id: int):
    try:
        material = await TrainingMaterial.get_or_none(id=id)
        if not material:
            raise HTTPException(status_code=404, detail="Training material not found")
        await delete_file(material.key)
        await material.delete()
        return {"message": "Training material deleted successfully"}


    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))