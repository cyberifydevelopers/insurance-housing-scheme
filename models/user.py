from enum import Enum
from tortoise.models import Model
from tortoise import fields
import models


class UserType(str, Enum):
    ADMIN = "admin"
    USER = "user"

class User(Model):
    id = fields.IntField(primary_key=True)
    name = fields.CharField(max_length=255)
    email = fields.CharField(max_length=255)
    password = fields.CharField(max_length=255)
    type = fields.CharEnumField(UserType, max_length=10)
    course_tracker = fields.JSONField(null=True)
