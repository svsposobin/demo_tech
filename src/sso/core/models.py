from datetime import datetime
from decimal import Decimal
from typing import Optional, Dict

from pydantic import BaseModel

from src.sso.core.cookies import CookiesConfig


class UserAccount(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    balance: Optional[Decimal] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    is_active: Optional[int] = None


class BaseUserInfo(BaseModel):
    id: Optional[int] = None
    email: Optional[str] = None
    full_name: Optional[str] = None


class ErrorDetail(BaseModel):
    detail: str
    status_code: int


class UserSessionResponse(BaseModel):
    session_token: Optional[str] = None
    active_session: bool = False
    user_id: Optional[int] = None

    error: Optional[ErrorDetail] = None


class UserLoginResponse(BaseModel):
    cookies: Optional[CookiesConfig] = None

    error: Optional[ErrorDetail] = None
    success_detail: Optional[Dict[str, str]] = None


class RemoveUserSessionsResponse(BaseModel):
    detail: Optional[str] = None

    error: Optional[ErrorDetail] = None


class LogoutResponse(BaseModel):
    detail: Optional[str] = None

    error: Optional[ErrorDetail] = None
