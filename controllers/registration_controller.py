from fastapi import APIRouter, File, Form, UploadFile, HTTPException, Depends
from typing import Optional
import random
import string
from models.user import User, UserType
from models.user_registration import UserRegistration
from helpers.email_service import EmailService
from helpers.s3_helper import S3Helper
from helpers.get_current_user import get_current_user
from argon2 import PasswordHasher

router = APIRouter(prefix="/api")
email_service = EmailService()
s3_helper = S3Helper()

def generate_password(length=12):
    """Generate a random password"""
    characters = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(random.choice(characters) for _ in range(length))

ph = PasswordHasher()

def hash_password(password: str) -> str:
    """Hash a password using Argon2"""
    return ph.hash(password)

@router.post("/register")
async def register_user(
    full_name: str = Form(...),
    email: str = Form(...),
    resume: UploadFile = File(...),
    utm_source: Optional[str] = Form(None),
    utm_medium: Optional[str] = Form(None),
    utm_campaign: Optional[str] = Form(None),
    utm_term: Optional[str] = Form(None),
    utm_content: Optional[str] = Form(None),
    metadata: Optional[str] = Form(None)
):
    # Check if user already exists
    existing_user = await User.filter(email=email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Generate random password
    password = generate_password()
    hashed_password = hash_password(password)

    # Create user
    user = await User.create(
        name=full_name,
        email=email,
        password=hashed_password,
        type=UserType.USER
    )

    # Upload resume to S3
    file_extension = resume.filename.split('.')[-1]
    s3_path = f"resumes/{user.id}/{user.id}_resume.{file_extension}"
    
    try:
        if not s3_helper.upload_file(resume.file, s3_path, resume.content_type):
            await user.delete()
            raise HTTPException(status_code=500, detail="Failed to upload resume")

    except Exception as e:
        await user.delete()
        raise HTTPException(status_code=500, detail="Failed to upload resume")

    # Create user registration record
    try:
        await UserRegistration.create(
            user=user,
            resume_path=s3_path,
            utm_source=utm_source,
            utm_medium=utm_medium,
            utm_campaign=utm_campaign,
            utm_term=utm_term,
            utm_content=utm_content,
            metadata=metadata
        )
    except Exception as e:
        await user.delete()
        # Delete uploaded file from S3
        s3_helper.delete_file(s3_path)
        raise HTTPException(status_code=500, detail="Failed to create registration record")

    # Send welcome email
    try:
        email_service.send_welcome_email(
            to_email=email,
            name=full_name,
            password=password,
            user_id=user.id
        )
    except Exception as e:
        # Don't delete the user account if email fails
        # Just log the error (you should add proper logging)
        print(f"Failed to send welcome email: {str(e)}")

    return {"message": "Registration successful", "user_id": user.id}

@router.get("/resume/{user_id}")
async def get_resume_url(user_id: int, current_user: User = Depends(get_current_user)):
    """Get a pre-signed URL for downloading a user's resume"""
    # Only allow admin or the user themselves to access the resume
    if current_user.type != UserType.ADMIN and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this resume")

    # Get the user registration record
    registration = await UserRegistration.filter(user_id=user_id).first()
    if not registration:
        raise HTTPException(status_code=404, detail="Resume not found")

    # Generate a pre-signed URL valid for 1 hour
    download_url = s3_helper.get_download_url(registration.resume_path, expiration=3600)
    if not download_url:
        raise HTTPException(status_code=500, detail="Failed to generate resume download URL")

    return {
        "download_url": download_url,
        "file_name": registration.resume_path.split('/')[-1],
        "expires_in": "1 hour"
    }