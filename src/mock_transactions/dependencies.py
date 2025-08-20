from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from databases.postgres.utils import async_db_session
from src.mock_transactions.models import PaymentWebhookData, PaymentProcessResponse
from src.mock_transactions.payment_processor import PaymentProcessor
from src.mock_transactions.constants import SECRET_PAYMENT_KEY
from src.mock_transactions.utils import mock_payment_data


async def mock_handle_input_transaction(
        db_session: AsyncSession = Depends(async_db_session),
        mock_webhook_data: PaymentWebhookData = Depends(mock_payment_data)
) -> PaymentProcessResponse:
    async with db_session.begin():
        payment_processor: PaymentProcessor = PaymentProcessor(
            secret_payment_key=SECRET_PAYMENT_KEY,
            db_session=db_session,
        )

        result: PaymentProcessResponse = await payment_processor.process(data=mock_webhook_data)

        return result
