from datetime import datetime, timedelta, timezone
from typing import Annotated, Optional

from fastapi import Depends, Form, Cookie, Response
from pydantic import EmailStr
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from databases.postgres.models import Users, UsersSessions
from databases.postgres.utils import async_db_session
from src.sso.core.cookies import CookiesConfig
from src.sso.core.models import (
    UserLoginResponse,
    UserSessionResponse,
    ErrorDetail,
    RemoveUserSessionsResponse,
    LogoutResponse
)
from src.sso.core.constants import COOKIE_AUTH_KEY, COOKIE_SESSION_EXPIRE_MINUTES
from src.sso.core.utils import generate_session_token
from src.utils import check_password


async def check_active_session(
        response: Response,
        session_token: Optional[str] = Cookie(default=None, alias=COOKIE_AUTH_KEY),
        db_session: AsyncSession = Depends(async_db_session)
) -> UserSessionResponse:
    result: UserSessionResponse = UserSessionResponse()

    try:
        if not session_token:
            result.error = ErrorDetail(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Session not found",
            )

            return result

        user_session: Optional[UsersSessions] = await db_session.scalar(
            select(UsersSessions).where(
                UsersSessions.session_token == session_token,
                UsersSessions.expires_at > datetime.now(timezone.utc).replace(tzinfo=None)  # Ищем active-сессии
            )
        )
        if not user_session:
            response.delete_cookie(key=COOKIE_AUTH_KEY)  # Опционально, удаляем невалидный токен

            result.error = ErrorDetail(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session expired or not found",
            )

            return result

        result.active_session = True
        result.session_token = user_session.session_token
        result.user_id = user_session.user_id

    except Exception as error:
        result.error = ErrorDetail(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Oops, something went wrong! {error}",
        )

    return result


async def login(
        email: Annotated[EmailStr, Form()],
        password: Annotated[str, Form()],
        user_session: UserSessionResponse = Depends(check_active_session),
        db_session: AsyncSession = Depends(async_db_session),
) -> UserLoginResponse:
    result: UserLoginResponse = UserLoginResponse()

    try:
        if user_session.active_session is True:
            result.error = ErrorDetail(
                status_code=status.HTTP_303_SEE_OTHER,
                detail="The user has an active session",
            )

            return result

        user: Optional[Users] = await db_session.scalar(
            select(Users).where(Users.email == email)
        )
        if not user:
            result.error = ErrorDetail(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="The user does not exist",
            )

            return result

        if not check_password(password=password, hashed_password=user.hash_password):
            result.error = ErrorDetail(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

            return result

        session_token: str = generate_session_token()
        new_session: UsersSessions = UsersSessions.create_with_lifetime(
            user_id=user.id,
            session_token=session_token,
        )
        db_session.add(new_session)
        await db_session.commit()

        result.cookies = CookiesConfig(
            KEY=COOKIE_AUTH_KEY,
            VALUE=session_token,
            EXPIRES=datetime.now(timezone.utc) + timedelta(minutes=COOKIE_SESSION_EXPIRE_MINUTES),
        )
        result.success_detail = {"detail": "Login successful"}

    except Exception as error:
        await db_session.rollback()
        result.error = ErrorDetail(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Oops, something went wrong! {error}",
        )

    return result


async def remove_all_session(
        response: Response,
        session_token: Optional[str] = Cookie(default=None, alias=COOKIE_AUTH_KEY),
        db_session: AsyncSession = Depends(async_db_session),
) -> RemoveUserSessionsResponse:
    result: RemoveUserSessionsResponse = RemoveUserSessionsResponse()

    try:
        if not session_token:
            result.detail = "Session not found"

            return result

        user: Optional[UsersSessions] = await db_session.scalar(
            select(UsersSessions).where(UsersSessions.session_token == session_token)
        )

        if not user:
            response.delete_cookie(key=COOKIE_AUTH_KEY)

            result.detail = "Session not found"

            return result

        await db_session.execute(
            delete(UsersSessions).where(UsersSessions.user_id == user.user_id)
        )
        await db_session.commit()

        response.delete_cookie(key=COOKIE_AUTH_KEY)

        result.detail = "All sessions deleted!"

    except Exception as error:
        await db_session.rollback()
        result.error = ErrorDetail(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Oops, something went wrong! {error}",
        )

    return result


async def logout(
        response: Response,
        db_session: AsyncSession = Depends(async_db_session),
        user_session: UserSessionResponse = Depends(check_active_session)
) -> LogoutResponse:
    result: LogoutResponse = LogoutResponse()

    try:
        if user_session.active_session is False:
            result.error = ErrorDetail(
                status_code=user_session.error.status_code,  # type: ignore
                detail=user_session.error.detail,  # type: ignore
            )

            return result

        await db_session.execute(
            delete(UsersSessions).where(UsersSessions.session_token == user_session.session_token)
        )
        await db_session.commit()

        response.delete_cookie(key=COOKIE_AUTH_KEY)

        result.detail = "Logout successful"

    except Exception as error:
        await db_session.rollback()
        result.error = ErrorDetail(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Oops, something went wrong! {error}",
        )

    return result
