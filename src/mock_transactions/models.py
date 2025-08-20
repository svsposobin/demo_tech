from decimal import Decimal
from typing import Optional

from pydantic import BaseModel

from src.sso.core.models import ErrorDetail


class PaymentWebhookData(BaseModel):
    transaction_id: str
    account_id: int
    user_id: int
    amount: Decimal
    signature: str


class AccountExistsResponse(BaseModel):
    correct_account_id: Optional[int] = None
    detail: Optional[str] = None


class PaymentProcessResponse(BaseModel):
    error: Optional[ErrorDetail] = None
    detail: Optional[str] = None
