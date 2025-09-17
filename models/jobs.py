import models 
from tortoise.models import Model
from tortoise import fields  

class Job(Model):
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=100)
    jobs = fields.JSONField()
