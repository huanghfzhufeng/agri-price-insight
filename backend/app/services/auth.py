from __future__ import annotations

from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import calculate_expiry, generate_access_token, verify_password
from app.models.entities import AuthToken, User
from app.schemas.auth import LoginResponse, UserProfile


settings = get_settings()


def authenticate_user(db: Session, username: str, password: str) -> User:
    user = db.scalar(select(User).where(User.username == username.strip()))
    if user is None or not user.is_active or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误。")
    return user


def login_user(db: Session, username: str, password: str) -> LoginResponse:
    user = authenticate_user(db, username=username, password=password)
    token = generate_access_token()
    expires_at = calculate_expiry(settings.auth_token_ttl_hours)

    db.add(AuthToken(user_id=user.id, token=token, expires_at=expires_at, last_used_at=datetime.now()))
    user.last_login_at = datetime.now()
    db.commit()
    db.refresh(user)

    return LoginResponse(
        access_token=token,
        expires_at=expires_at,
        user=UserProfile(
            id=user.id,
            username=user.username,
            display_name=user.display_name,
            role=user.role,
            last_login_at=user.last_login_at,
        ),
    )


def logout_user(db: Session, token: str) -> None:
    auth_token = db.scalar(select(AuthToken).where(AuthToken.token == token))
    if auth_token is None:
        return
    db.delete(auth_token)
    db.commit()
