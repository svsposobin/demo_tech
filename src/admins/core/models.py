from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel

from src.sso.core.models import ErrorDetail, BaseUserInfo, UserAccount


class UserWithAccount(BaseUserInfo):
    role_id: Optional[int] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    accounts: Optional[List[UserAccount]] = None


class AdminInfoSessionResponse(BaseModel):
    user: Optional[BaseUserInfo] = None
    error: Optional[ErrorDetail] = None


class CreateUserResponse(BaseModel):
    detail: Optional[str] = None
    new_user_id: Optional[int] = None
    error: Optional[ErrorDetail] = None


class DeleteUserResponse(BaseModel):
    detail: Optional[str] = None
    error: Optional[ErrorDetail] = None


class UpdateUserResponse(BaseModel):
    detail: Optional[str] = None
    updated_user_id: Optional[int] = None

    error: Optional[ErrorDetail] = None


class UsersWithAccountsResponse(BaseModel):
    users: Optional[List[UserWithAccount]] = []
    page: Optional[int] = None
    max_user_per_page: Optional[int] = None

    error: Optional[ErrorDetail] = None
