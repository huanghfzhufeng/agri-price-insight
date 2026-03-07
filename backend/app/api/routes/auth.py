from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.api.deps import bearer_scheme, require_authenticated_user
from app.db.session import get_db
from app.models.entities import User
from app.schemas.auth import LoginRequest
from app.services.auth import login_user, logout_user

router = APIRouter()


@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    return login_user(db, username=payload.username, password=payload.password)


@router.get("/me")
def current_user(user: User = Depends(require_authenticated_user)):
    return {
        "id": user.id,
        "username": user.username,
        "display_name": user.display_name,
        "role": user.role,
        "last_login_at": user.last_login_at,
    }


@router.post("/logout")
def logout(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    _user: User = Depends(require_authenticated_user),
    db: Session = Depends(get_db),
):
    if credentials is not None:
        logout_user(db, credentials.credentials)
    return {"message": "已退出登录"}
