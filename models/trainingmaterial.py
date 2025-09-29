from enum import Enum
from tortoise.models import Model
from tortoise import fields
from models.jobs import Job

class TrainingMaterial(Model):
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=255, null=True)
    type = fields.CharField(max_length=20)
    file_url = fields.CharField(max_length=255, null=True)
    key = fields.CharField(max_length=255, null=True)
    step = fields.ForeignKeyField(
        "models.Step", related_name="training_materials", on_delete=fields.CASCADE
    )
    course = fields.ForeignKeyField(
        "models.Course", related_name="course_training_materials", on_delete=fields.CASCADE
    )