from typing import Annotated
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt
import os
from models.user import User
from typing import Any

security = HTTPBearer()

async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
):
    try:
        token = credentials.credentials
        decoded_token = jwt.decode(token, os.environ.get("JWT_SECRET"), algorithms=["HS256"])
        user_id = decoded_token["id"]
        user = await User.get(id=user_id)
        return user
    except:
        raise HTTPException(
            401,
            "Unauthorized"
        )

CurrentUser = Annotated[User, Depends(get_current_user)]