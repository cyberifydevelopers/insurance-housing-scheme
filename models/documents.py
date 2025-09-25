from enum import Enum
from tortoise.models import Model
from tortoise import fields
from models.jobs import Job


class DocumentType(str, Enum):
    ODF = "pdf"
    VIDEO = "video"


class Documents(Model):
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=255, null=True)
    type = fields.CharEnumField(DocumentType, max_length=10)
    job: fields.ForeignKeyRelation[Job] = fields.ForeignKeyField(
        "models.Job", related_name="documents", on_delete=fields.CASCADE
    )
