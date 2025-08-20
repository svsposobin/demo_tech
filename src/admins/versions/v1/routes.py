from fastapi import APIRouter, Depends, HTTPException

from src.admins.core.models import (
    AdminInfoSessionResponse,
    CreateUserResponse,
    DeleteUserResponse,
    UpdateUserResponse,
    UsersWithAccountsResponse
)
from src.admins.versions.v1.dependencies import (
    admin_info_session as admin_info_session_dependency,
    create_user as create_user_dependency,
    delete_user as delete_user_dependency,
    update_user_by_email as update_user_by_email_dependency,
    get_users_with_accounts as get_users_with_accounts_dependency,
)

router: APIRouter = APIRouter(prefix="/api/v1/admins", tags=["ADMINS_API_V1"])


@router.get(path="/me")
async def admin_info(
        result: AdminInfoSessionResponse = Depends(admin_info_session_dependency)
):
    if result.error:
        raise HTTPException(
            status_code=result.error.status_code,
            detail=result.error.detail,
        )

    return result.user


@router.post(path="/users/create-user")
async def create_user(
        result: CreateUserResponse = Depends(create_user_dependency)
):
    if result.error:
        raise HTTPException(
            status_code=result.error.status_code,
            detail=result.error.detail,
        )

    return result


@router.delete(path="/users/delete-user")
async def delete_user(
        result: DeleteUserResponse = Depends(delete_user_dependency)
):
    if result.error:
        raise HTTPException(
            status_code=result.error.status_code,
            detail=result.error.detail,
        )

    return result


@router.patch(path="/users/update-user")
async def update_user(
        result: UpdateUserResponse = Depends(update_user_by_email_dependency)
):
    if result.error:
        raise HTTPException(
            status_code=result.error.status_code,
            detail=result.error.detail,
        )

    return result


@router.get(path="/users-with-accounts")
async def users(
        result: UsersWithAccountsResponse = Depends(get_users_with_accounts_dependency)
):
    if result.error:
        raise HTTPException(
            status_code=result.error.status_code,
            detail=result.error.detail,
        )

    return result
