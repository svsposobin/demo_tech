from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel

from src.sso.core.models import ErrorDetail, BaseUserInfo, UserAccount


class Transaction(BaseModel):
    id: Optional[int] = None
    account_name: Optional[str] = None
    type: Optional[str] = None
    amount: Optional[float] = None
    status: Optional[str] = None
    external_id: Optional[str] = None
    created_at: Optional[datetime] = None


class UserInfoSessionResponse(BaseModel):
    user: Optional[BaseUserInfo] = None
    error: Optional[ErrorDetail] = None


class UserAccountsInfoResponse(BaseModel):
    accounts: Optional[List[UserAccount]] = []
    error: Optional[ErrorDetail] = None


class UserTransactionsInfoResponse(BaseModel):
    transactions: Optional[List[Transaction]] = []
    error: Optional[ErrorDetail] = None
