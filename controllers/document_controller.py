from fastapi import APIRouter
from models.documents import Documents
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Literal, Optional
from models.documents import Documents
from models.jobs import Job


router = APIRouter(prefix="/api/document")


class DocumentIn(BaseModel):
    id: int = 0
    title: str
    type: Literal["pdf", "video"]
    jobId: int


@router.post("/save")
async def save_document(doc: DocumentIn):
    if doc.id == 0:
        job = await Job.get_or_none(id=doc.jobId)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        await Documents.create(title=doc.title, type=doc.type, job=job)
        return {
            "message": "Document created successfully",
        }
    else:
        existing_doc = await Documents.get_or_none(id=doc.id)
        if not existing_doc:
            raise HTTPException(status_code=404, detail="Document not found")

        job = await Job.get_or_none(id=doc.jobId)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        existing_doc.title = doc.title
        existing_doc.type = doc.type
        existing_doc.job = job
        await existing_doc.save()
        return {
            "message": "Document updated successfully",
        }


@router.get("/get")
async def get_docs():
    documents = await Documents.all()
    result = []
    for doc in documents:
        job = await Job.filter(id=doc.job_id).first()
        result.append(
            {
                "id": doc.id,
                "title": doc.title,
                "type": doc.type,
                "job": {"id": job.id, "title": job.title} if job else None,
            }
        )
    return {"documents": result}


@router.delete("/delete/{id}")
async def delete_document(id: int):
    doc = await Documents.get_or_none(id=id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    await doc.delete()
    return {"message": "Document deleted successfully"}
