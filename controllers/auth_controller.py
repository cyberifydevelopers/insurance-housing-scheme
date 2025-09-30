from fastapi import APIRouter
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, EmailStr
from models.user import User
from argon2 import PasswordHasher
import jwt
import os
import datetime
from helpers.get_current_user import CurrentUser
import random
from pydantic import BaseModel
from fastapi import Request
from fastapi.responses import JSONResponse

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


@router.get("/me")
async def signup(user: CurrentUser):
    return {"data": user}


@router.get("/create-users")
async def create_users():
    created_users = []
    for _ in range(5):
        random_num = random.randint(1000, 9999)
        hashed_password = ph.hash("123456")
        user = await User.create(
            name=f"User{random_num}",
            email=f"user{random_num}@example.com",
            password=hashed_password,
            type="user",
        )
        created_users.append(
            {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "password": user.password,
                "type": user.type,
            }
        )

    return {"message": "5 users created", "users": created_users}


@router.post("/update-activity")
async def update_activity(request: Request, user: CurrentUser):
    db = user.course_tracker or {"courses": []}
    data = await request.json()

    for course_data in data.get("courses", []):
        course = next(
            (c for c in db["courses"] if c["id"] == course_data.get("id")), None
        )
        if not course:
            course = {
                "id": course_data.get("id"),
                "name": course_data.get("name"),
                "steps": [],
            }
            db["courses"].append(course)

        for step_data in course_data.get("steps", []):
            step = next(
                (s for s in course["steps"] if s["id"] == step_data.get("id")), None
            )
            if not step:
                step = {
                    "id": step_data.get("id"),
                    "name": step_data.get("name"),
                    "lessons": [],
                }
                course["steps"].append(step)

            for lesson_data in step_data.get("lessons", []):
                lesson = next(
                    (l for l in step["lessons"] if l["id"] == lesson_data.get("id")),
                    None,
                )
                if not lesson:
                    step["lessons"].append(
                        {"id": lesson_data.get("id"), "name": lesson_data.get("name")}
                    )

    user.course_tracker = db
    await user.save()

    return JSONResponse(content={"message": "Activity updated", "db": db})


@router.get("/get-users")
async def get_users():
    all_users = await User.filter(type="user").all()
    return {"users": all_users}
