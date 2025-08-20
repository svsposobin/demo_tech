"""
    Роут: register отсутствует сознательно
    Данная версия: демо (Тестовое)
    Создать пользователя можно только через администратора
"""
from fastapi import APIRouter, Depends, Response, HTTPException

from src.sso.core.models import UserLoginResponse, RemoveUserSessionsResponse, LogoutResponse
from src.sso.versions.v1.dependencies import (
    login as login_dependency,
    remove_all_session as remove_all_session_dependency,
    logout as logout_dependency
)
from src.sso.core.cookies import set_cookie

router: APIRouter = APIRouter(prefix="/api/v1/sso", tags=["SSO_API_V1"])


@router.post(path="/login")
async def login(
        response: Response,
        result: UserLoginResponse = Depends(login_dependency)
):
    if result.error:
        raise HTTPException(
            status_code=result.error.status_code,
            detail=result.error.detail,
        )

    set_cookie(response=response, cookie_config=result.cookies)  # type: ignore

    return result.success_detail


@router.delete(path="/sessions/remove-all")
async def remove_all_user_sessions(
        result: RemoveUserSessionsResponse = Depends(remove_all_session_dependency),
):
    return result


@router.post(path="/logout")
async def logout(
        result: LogoutResponse = Depends(logout_dependency)
):
    if result.error:
        raise HTTPException(
            status_code=result.error.status_code,
            detail=result.error.detail,
        )

    return result
