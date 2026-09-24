from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.db import get_user_by_session

bearer = HTTPBearer(auto_error=False)


def current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
) -> dict:
    token = credentials.credentials if credentials else ""
    user = get_user_by_session(token)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required.")
    return user
