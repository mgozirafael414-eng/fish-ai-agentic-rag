from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from app.auth import current_user
from app.db import (
    authenticate_user,
    create_session,
    create_user,
    delete_session,
    get_settings,
    update_profile,
    update_settings,
)

router = APIRouter(prefix="/api", tags=["Account"])
bearer = HTTPBearer(auto_error=False)


class RegisterRequest(BaseModel):
    email: str
    password: str
    display_name: str = ""


class LoginRequest(BaseModel):
    email: str
    password: str


class ProfileUpdate(BaseModel):
    display_name: str


class SettingsUpdate(BaseModel):
    dark_mode: bool


@router.post("/auth/register")
def register(request: RegisterRequest):
    if "@" not in request.email:
        raise HTTPException(status_code=400, detail="A valid email is required.")
    if len(request.password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters.")
    try:
        user = create_user(request.email, request.password, request.display_name)
    except Exception as error:
        if "UNIQUE constraint failed" in str(error):
            raise HTTPException(status_code=409, detail="An account with that email already exists.")
        raise HTTPException(status_code=500, detail="Could not create account.") from error
    return {"success": True, "user": user, "token": create_session(user["id"])}


@router.post("/auth/login")
def login(request: LoginRequest):
    user = authenticate_user(request.email, request.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    return {"success": True, "user": user, "token": create_session(user["id"])}


@router.post("/auth/logout")
def logout(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    user=Depends(current_user),
):
    if credentials:
        delete_session(credentials.credentials)
    return {"success": True, "message": "Logged out successfully."}


@router.get("/auth/me")
def me(user=Depends(current_user)):
    return {"success": True, "user": user}


@router.get("/profile")
def profile(user=Depends(current_user)):
    return {"success": True, "profile": user}


@router.patch("/profile")
def update_user_profile(request: ProfileUpdate, user=Depends(current_user)):
    if not request.display_name.strip():
        raise HTTPException(status_code=400, detail="Display name cannot be empty.")
    return {"success": True, "profile": update_profile(user["id"], request.display_name)}


@router.get("/settings")
def settings(user=Depends(current_user)):
    return {"success": True, "settings": get_settings(user["id"])}


@router.patch("/settings")
def update_user_settings(request: SettingsUpdate, user=Depends(current_user)):
    return {"success": True, "settings": update_settings(user["id"], request.dark_mode)}
