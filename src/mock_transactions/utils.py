from decimal import Decimal
from secrets import token_urlsafe
from hashlib import sha256 as hashlib_sha256
from typing import Annotated

from fastapi import Form

from src.mock_transactions.models import PaymentWebhookData
from src.mock_transactions.constants import SECRET_PAYMENT_KEY


async def mock_payment_data(
        account_id: Annotated[int, Form()],
        user_id: Annotated[int, Form()],
        amount: Annotated[str, Form()],
) -> PaymentWebhookData:
    mock_transaction_id = token_urlsafe(15)
    valid_signature: str = hashlib_sha256(
        string=f"{account_id}{amount}{mock_transaction_id}{user_id}{SECRET_PAYMENT_KEY}".encode()
    ).hexdigest().lower()

    return PaymentWebhookData(
        transaction_id=mock_transaction_id,
        account_id=account_id,
        user_id=user_id,
        amount=Decimal(amount),
        signature=valid_signature
    )
