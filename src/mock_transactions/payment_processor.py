from decimal import Decimal
from hashlib import sha256 as hashlib_sha256
from typing import Optional

from fastapi import status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from databases.postgres.models import Accounts, Transactions
from src.mock_transactions.models import PaymentWebhookData, PaymentProcessResponse, AccountExistsResponse
from src.sso.core.models import ErrorDetail


class PaymentProcessor:
    def __init__(self, secret_payment_key: str, db_session: AsyncSession) -> None:
        self.__payment_key = secret_payment_key
        self._db_session = db_session

    async def process(self, data: PaymentWebhookData) -> PaymentProcessResponse:
        """Обработка платежа: проверка счета, сохранение транзакции, начисление средств"""
        result: PaymentProcessResponse = PaymentProcessResponse()

        try:
            signature_verification: bool = await self._signature_authentication(data=data)

            if not signature_verification:
                result.error = ErrorDetail(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid signature"
                )
                return result

            account: AccountExistsResponse = await self._account_exists(
                payment_data=data,
                account_name=f"user_account: {data.user_id}"  # В качестве генерации тестового имени
            )

            account_obj = await self._db_session.get(Accounts, account.correct_account_id)
            new_transaction: Transactions = Transactions(
                account_id=account.correct_account_id,
                type="debit",  # В качестве тестового, жестко "захардкоден"
                amount=data.amount,
                status="pending",
                external_id=data.transaction_id,
            )
            self._db_session.add(new_transaction)

            account_obj.balance += data.amount  # type: ignore
            new_transaction.status = "completed"

            result.detail = f"{account.detail}. The amount was charged: {data.amount}"

        except IntegrityError:
            result.error = ErrorDetail(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Transaction with ID {data.transaction_id} already exists",
            )

        except Exception as error:
            result.error = ErrorDetail(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Oops, something went wrong! {error}",
            )

        return result

    async def _signature_authentication(self, data: PaymentWebhookData) -> bool:
        """Проверка подписи"""
        signature: str = hashlib_sha256(
            string=f"{data.account_id}{data.amount}{data.transaction_id}{data.user_id}{self.__payment_key}".encode()
        ).hexdigest().lower()

        return signature == data.signature

    async def _account_exists(
            self,
            payment_data: PaymentWebhookData,
            account_name: str,
    ) -> AccountExistsResponse:
        result: AccountExistsResponse = AccountExistsResponse()

        user_account: Optional[int] = await self._db_session.scalar(
            select(Accounts.id).where(
                Accounts.id == payment_data.account_id,
                Accounts.user_id == payment_data.user_id
            )
        )
        if not user_account:
            new_account: Accounts = Accounts(
                user_id=payment_data.user_id,
                name=account_name,
                balance=Decimal(0),
            )

            self._db_session.add(new_account)
            await self._db_session.flush()

            account_id: int = new_account.id
            result.detail = "A new account has been created"

        else:
            account_id = user_account
            result.detail = "User account found"

        result.correct_account_id = account_id

        return result
