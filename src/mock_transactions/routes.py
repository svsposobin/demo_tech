from fastapi import APIRouter, Depends, HTTPException

from src.mock_transactions.dependencies import mock_handle_input_transaction as mock_handle_input_transaction_dependency
from src.mock_transactions.models import PaymentProcessResponse

router = APIRouter(tags=["TEST_PAYMENT_WEBHOOK"])


@router.post(
    path="/handle-test-payment",
    description="Тестовая обработка транзакции от мок-вебхука. "
                "id-транзакции и валидная подпись генерируются 'под капотом'"
)
async def handle_test_payment(
        result: PaymentProcessResponse = Depends(mock_handle_input_transaction_dependency)
):
    if result.error:
        raise HTTPException(
            status_code=result.error.status_code,
            detail=result.error.detail
        )

    return result
