from tortoise.models import Model
from tortoise import fields
from .user import User

class UserRegistration(Model):
    id = fields.IntField(primary_key=True)
    user = fields.ForeignKeyField('models.User', related_name='registration_data')
    resume_path = fields.CharField(max_length=512)  # Path to resume in S3
    utm_source = fields.CharField(max_length=255, null=True)
    utm_medium = fields.CharField(max_length=255, null=True)
    utm_campaign = fields.CharField(max_length=255, null=True)
    utm_term = fields.CharField(max_length=255, null=True)
    utm_content = fields.CharField(max_length=255, null=True)
    metadata = fields.JSONField(null=True)  # For any additional metadata
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "user_registrations"