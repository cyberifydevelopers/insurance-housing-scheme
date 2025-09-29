from tortoise import fields
from tortoise.models import Model

class Step(Model):
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=255)
    order = fields.IntField(default=0)
    
    course = fields.ForeignKeyField(
        "models.Course", related_name="steps", on_delete=fields.CASCADE
    )