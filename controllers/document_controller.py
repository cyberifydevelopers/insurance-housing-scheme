from fastapi import APIRouter
from models.documents import Documents
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Literal, Optional
from models.documents import Documents
from models.jobs import Job
from fastapi import APIRouter, File, Form, UploadFile, HTTPException
import shutil
import uuid
import os
import aioboto3
from typing import List
from helpers.files import delete_file

router = APIRouter(prefix="/api/document")


class DocumentIn(BaseModel):
    id: int
    title: str
    videos: list
    pdfs: list


@router.post("/save")
async def save_document(doc: DocumentIn):
    if doc.id == 0:
        document = await Documents.create(
            title=doc.title, videos=doc.videos, pdf=doc.pdfs
        )
        return {"message": "Document created successfully", "document_id": document.id}
    else:
        existing_doc = await Documents.get_or_none(id=doc.id)
        if not existing_doc:
            raise HTTPException(status_code=404, detail="Document not found")
        existing_doc.title = doc.title
        existing_doc.videos = doc.videos
        existing_doc.pdf = doc.pdfs
        await existing_doc.save()
        return {
            "message": "Document updated successfully",
            "document_id": existing_doc.id,
        }


@router.get("/get")
async def get_docs():
    documents = await Documents.all()
    result = []
    for doc in documents:
        result.append(
            {
                "id": doc.id,
                "title": doc.title,
                "videos": doc.videos or [],  
                "pdfs": doc.pdf or [], 
            }
        )
    return {"documents": result}


@router.delete("/delete/{id}")
async def delete_document(id: int):
    doc = await Documents.get_or_none(id=id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if doc.videos:
        for video in doc.videos:
            await delete_file(video["key"])
    if doc.pdf:
        for pdf in doc.pdf:
            await delete_file(pdf["key"])
    await doc.delete()
    return {"message": "Traning material deleted successfully"}


@router.post("/upload-file")
async def upload_file(file: UploadFile = File(...), folder_name: str = Form(...)):
    try:
        ext = os.path.splitext(file.filename)[1]
        unique_name = f"{uuid.uuid4().hex}{ext}"
        s3_key = f"{folder_name}/{unique_name}"
        bucket_name = os.environ.get("BUCKET_NAME")
        region = os.environ.get("AWS_REGION")

        session = aioboto3.Session()
        async with session.client(
            "s3",
            aws_access_key_id=os.environ.get("AWS_ACCESS_KEY"),
            aws_secret_access_key=os.environ.get("AWS_SECRET_KEY"),
            region_name=region,
        ) as s3_client:
            await s3_client.put_object(
                Bucket=bucket_name,
                Key=s3_key,
                Body=await file.read(),  
                ContentType=file.content_type or "application/octet-stream",
            )
        file_url = f"https://{bucket_name}.s3.{region}.amazonaws.com/{s3_key}"
        return {
            "success": True,
            "message": f"File '{file.filename}' uploaded successfully as '{unique_name}'.",
            "file_url": file_url,
            "key": s3_key,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
