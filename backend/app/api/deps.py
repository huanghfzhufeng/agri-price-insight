from __future__ import annotations

from datetime import datetime

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.entities import AuthToken, User


bearer_scheme = HTTPBearer(auto_error=False)


def require_authenticated_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="请先登录后再访问。")

    auth_token = db.scalar(select(AuthToken).where(AuthToken.token == credentials.credentials))
    if auth_token is None or auth_token.expires_at <= datetime.now():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="登录态已失效，请重新登录。")

    user = db.scalar(select(User).where(User.id == auth_token.user_id, User.is_active.is_(True)))
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="当前账号不可用。")

    auth_token.last_used_at = datetime.now()
    db.commit()
    db.refresh(user)
    return user
