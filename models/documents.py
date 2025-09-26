from enum import Enum
from tortoise.models import Model
from tortoise import fields
from models.jobs import Job


class Documents(Model):
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=255, null=True)
    videos = fields.JSONField(default=list, null=True)
    pdf = fields.JSONField(default=list, null=True)
