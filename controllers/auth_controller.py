from fastapi import APIRouter
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, EmailStr
from models.user import User
from argon2 import PasswordHasher
import jwt
import os
import datetime

router = APIRouter(prefix="/api/auth")
ph = PasswordHasher()


class LoginPayload(BaseModel):
    email: EmailStr
    password: str = Field(max_length=255, min_length=2)


@router.get("/create-admin")
async def signup():
    admin_exists = await User.filter(email="admin@gmail.com").first()
    if admin_exists:
        raise HTTPException(400, "Admin already exists.")
    new_admin = await User.create(
        name="admin",
        email="admin@gmail.com",
        password=ph.hash("123456"),
        type="admin",
    )
    return {"success": True, "message": "Admin created succesfully.", "data": new_admin}


@router.post("/login")
async def login(data: LoginPayload):
    user = await User.filter(email=data.email).first()
    if not user:
        raise HTTPException(400, "Invalid email or password.")
    try:
        ph.verify(user.password, data.password)
    except:
        raise HTTPException(400, "Invalid email or password.")
    return {
        "success": True,
        "message": "You're loggedin successfully",
        "token": jwt.encode(
            {"id": user.id, "generated_at": str(datetime.datetime.now())},
            os.environ.get("JWT_SECRET"),
            algorithm="HS256",
        ),
        "userType": user.type,
    }
