from fastapi import APIRouter, Depends, HTTPException

from src.users.core.models import (
    UserInfoSessionResponse,
    UserAccountsInfoResponse,
    UserTransactionsInfoResponse
)
from src.users.versions.v1.dependencies import (
    user_info_session as user_info_session_dependency,
    get_accounts_with_balances as get_accounts_with_balances_dependency,
    get_transactions as get_transactions_dependency
)

router = APIRouter(prefix="/api/v1/users", tags=["USERS_API_V1"])


@router.get(path="/me")
async def user_info(
        result: UserInfoSessionResponse = Depends(user_info_session_dependency)
):
    if result.error:
        raise HTTPException(
            status_code=result.error.status_code,
            detail=result.error.detail,
        )

    return result.user


@router.get(path="/accounts")
async def user_accounts(
        result: UserAccountsInfoResponse = Depends(get_accounts_with_balances_dependency)
):
    if result.error:
        raise HTTPException(
            status_code=result.error.status_code,
            detail=result.error.detail,
        )

    return result.accounts


@router.get(path="/transactions")
async def user_transactions(
        result: UserTransactionsInfoResponse = Depends(get_transactions_dependency)
):
    if result.error:
        raise HTTPException(
            status_code=result.error.status_code,
            detail=result.error.detail,
        )

    return result
