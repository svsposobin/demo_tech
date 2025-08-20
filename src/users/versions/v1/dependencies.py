from typing import Tuple, Optional, Any

from fastapi import Depends, status, Query
from sqlalchemy import Result, select, Row, ScalarResult
from sqlalchemy.ext.asyncio import AsyncSession

from databases.postgres.models import Users, Accounts, Transactions
from databases.postgres.utils import async_db_session
from src.sso.core.models import UserSessionResponse, ErrorDetail, BaseUserInfo, UserAccount
from src.sso.versions.v1.dependencies import check_active_session
from src.users.core.constants import USER_ROLE_ID, TRANSACTIONS_PER_PAGE
from src.users.core.models import UserInfoSessionResponse, UserAccountsInfoResponse, UserTransactionsInfoResponse, \
    Transaction


async def user_info_session(  # Админ не может получить доступ к юзеру напрямую из домена users!
        user_session: UserSessionResponse = Depends(check_active_session),
        db_session: AsyncSession = Depends(async_db_session)
) -> UserInfoSessionResponse:
    result: UserInfoSessionResponse = UserInfoSessionResponse()

    try:
        if user_session.active_session is False:
            result.error = ErrorDetail(
                status_code=user_session.error.status_code,  # type: ignore
                detail=user_session.error.detail  # type: ignore
            )
            return result

        user: Result[Tuple] = await db_session.execute(
            select(Users.id, Users.email, Users.first_name, Users.last_name).where(
                Users.id == user_session.user_id,
                Users.role_id == USER_ROLE_ID
            )
        )
        user_data: Optional[Row[Tuple[Any]]] = user.first()

        if not user_data:
            result.error = ErrorDetail(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User not found"
            )
            return result

        user_id, email, first_name, last_name = user_data

        result.user = BaseUserInfo(
            id=user_id,
            email=email,
            full_name=f"{first_name} {last_name}" if last_name else first_name,
        )

    except Exception as error:
        result.error = ErrorDetail(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Oops, something went wrong! {error}",
        )

    return result


async def get_accounts_with_balances(
        user_session: UserInfoSessionResponse = Depends(user_info_session),
        db_session: AsyncSession = Depends(async_db_session)
) -> UserAccountsInfoResponse:
    result: UserAccountsInfoResponse = UserAccountsInfoResponse()

    try:
        if user_session.error:
            result.error = ErrorDetail(
                status_code=user_session.error.status_code,  # type: ignore
                detail=user_session.error.detail  # type: ignore
            )
            return result

        user_accounts: ScalarResult[Accounts] = await db_session.scalars(
            select(Accounts)
            .where(Accounts.user_id == user_session.user.id)  # type: ignore
            .order_by(Accounts.created_at)
        )

        for account in user_accounts.all():
            result.accounts.append(  # type: ignore
                UserAccount(
                    id=account.id,
                    name=account.name,
                    balance=account.balance,
                    created_at=account.created_at,
                    is_active=account.is_active,
                )
            )

    except Exception as error:
        result.error = ErrorDetail(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Oops, something went wrong! {error}",
        )

    return result


async def get_transactions(
        page: int = Query(default=1),
        user_session: UserInfoSessionResponse = Depends(user_info_session),
        db_session: AsyncSession = Depends(async_db_session)
) -> UserTransactionsInfoResponse:
    """Упрощенная реализация"""
    result: UserTransactionsInfoResponse = UserTransactionsInfoResponse()

    try:
        if user_session.error:
            result.error = ErrorDetail(
                status_code=user_session.error.status_code,
                detail=user_session.error.detail
            )
            return result

        if page <= 0:
            result.error = ErrorDetail(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Page number must be greater than 0",
            )
            return result

        limit: int = TRANSACTIONS_PER_PAGE
        offset: int = (page - 1) * limit

        transactions = await db_session.execute(
            select(Transactions, Accounts.name.label("account_name"))
            .join(Accounts, Transactions.account_id == Accounts.id)
            .where(Accounts.user_id == user_session.user.id)  # type: ignore
            .order_by(Transactions.created_at.desc())
            .limit(limit)
            .offset(offset)
        )

        for transaction, account_name in transactions.all():
            result.transactions.append(  # type: ignore
                Transaction(
                    id=transaction.id,
                    account_name=account_name,
                    type=transaction.type,
                    amount=float(transaction.amount),
                    status=transaction.status,
                    external_id=transaction.external_id,
                    created_at=transaction.created_at
                )
            )

    except Exception as error:
        result.error = ErrorDetail(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Oops, something went wrong! {error}",
        )

    return result
