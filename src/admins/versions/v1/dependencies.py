from typing import Tuple, Annotated, Optional, Dict, Any

from fastapi import Depends, status, Form, Query
from sqlalchemy import select, Result, Row, delete, CursorResult, update, ScalarResult
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from databases.postgres.models import Users
from databases.postgres.utils import async_db_session
from src.admins.core.constants import ADMIN_ROLE_ID, USERS_PER_PAGE
from src.admins.core.models import (
    AdminInfoSessionResponse,
    CreateUserResponse,
    DeleteUserResponse,
    UpdateUserResponse,
    UserWithAccount,
    UsersWithAccountsResponse, UserAccount

)
from src.sso.core.models import ErrorDetail, UserSessionResponse, BaseUserInfo
from src.sso.versions.v1.dependencies import check_active_session
from src.utils import hash_password


async def admin_info_session(
        user_session: UserSessionResponse = Depends(check_active_session),
        db_session: AsyncSession = Depends(async_db_session)
) -> AdminInfoSessionResponse:
    result: AdminInfoSessionResponse = AdminInfoSessionResponse()

    try:
        if user_session.active_session is False:
            result.error = ErrorDetail(
                status_code=user_session.error.status_code,  # type: ignore
                detail=user_session.error.detail,  # type: ignore
            )

            return result

        admin: Result[Tuple] = await db_session.execute(
            select(Users.id, Users.email, Users.first_name, Users.last_name).where(
                Users.id == user_session.user_id,
                Users.role_id == ADMIN_ROLE_ID
            )
        )
        admin_data: Optional[Row[Tuple[Any]]] = admin.first()

        if not admin_data:
            result.error = ErrorDetail(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User not found or user is not an administrator"
            )

            return result

        user_id, email, first_name, last_name = admin_data

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


async def create_user(
        email: Annotated[str, Form()],
        role_id: Annotated[int, Form()],
        password: Annotated[str, Form()],
        first_name: Annotated[str, Form()],
        last_name: Annotated[Optional[str], Form()] = None,
        admin_session: UserSessionResponse = Depends(admin_info_session),
        db_session: AsyncSession = Depends(async_db_session)
) -> CreateUserResponse:
    """
        Создание пользователей (Только для роли admin)
        Сознательно упрощено в качестве демо (Тестового):
         - Отсутствуют regex-паттерны валидации полей (+ Валидация в принципе);
         - Отсутствует корректная обработка ошибок (В данное время общая для всех)
    """
    result: CreateUserResponse = CreateUserResponse()

    try:
        if admin_session.error:
            result.error = ErrorDetail(
                status_code=admin_session.error.status_code,
                detail=admin_session.error.detail,
            )
            return result

        new_user: Users = Users(
            email=email,
            role_id=role_id,
            first_name=first_name,
            last_name=last_name,
            hash_password=hash_password(password=password)
        )
        db_session.add(new_user)

        await db_session.commit()
        await db_session.refresh(new_user)

        result.detail = "New user created!"
        result.new_user_id = new_user.id

    except IntegrityError:
        await db_session.rollback()
        result.error = ErrorDetail(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is registered or field failed validation",
        )

    except Exception as error:
        await db_session.rollback()
        result.error = ErrorDetail(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Oops, something went wrong! {error}",
        )

    return result


async def delete_user(
        email: Annotated[str, Form()],
        admin_session: UserSessionResponse = Depends(admin_info_session),
        db_session: AsyncSession = Depends(async_db_session)
) -> DeleteUserResponse:
    """
        Упрощенная реализация удаление пользователей по email (Демо в качестве тестового):
         - Отсутствует точная обработка ошибок
    """
    result: DeleteUserResponse = DeleteUserResponse()

    try:
        if admin_session.error:
            result.error = ErrorDetail(
                status_code=admin_session.error.status_code,
                detail=admin_session.error.detail,
            )
            return result

        remove_user: CursorResult = await db_session.execute(
            delete(Users).where(Users.email == email)
        )
        await db_session.commit()

        if remove_user.rowcount == 0:
            result.error = ErrorDetail(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User with this email not found",
            )

            return result

        result.detail = f"User with email {email} successfully deleted"

    except Exception as error:
        await db_session.rollback()
        result.error = ErrorDetail(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Oops, something went wrong! {error}",
        )

    return result


async def update_user_by_email(
        user_email: Annotated[str, Form()],
        new_email: Annotated[Optional[str], Form()] = None,
        new_role_id: Annotated[Optional[int], Form()] = None,
        new_first_name: Annotated[Optional[str], Form()] = None,
        new_last_name: Annotated[Optional[str], Form()] = None,
        new_password: Annotated[Optional[str], Form()] = None,
        admin_session: UserSessionResponse = Depends(admin_info_session),
        db_session: AsyncSession = Depends(async_db_session)
) -> UpdateUserResponse:
    """Упрощено без валидации полей"""
    result: UpdateUserResponse = UpdateUserResponse()

    try:
        updated_data: Dict[str, Any] = {}

        if admin_session.error:
            result.error = ErrorDetail(
                status_code=admin_session.error.status_code,
                detail=admin_session.error.detail,
            )

            return result

        # Упрощенная реализация
        if new_email is not None and new_email.strip() != "":
            updated_data["email"] = new_email
        if new_role_id is not None:
            updated_data["role_id"] = new_role_id
        if new_first_name is not None and new_first_name.strip() != "":
            updated_data["first_name"] = new_first_name
        if new_last_name is not None and new_last_name.strip() != "":
            updated_data["last_name"] = new_last_name
        if new_password is not None and new_password.strip() != "":
            updated_data["hash_password"] = hash_password(new_password)

        if not updated_data:
            result.detail = "No fields to update"
            return result

        update_result: Optional[int] = await db_session.scalar(
            update(Users)
            .where(Users.email == user_email)
            .values(**updated_data)
            .returning(Users.id)
        )
        await db_session.commit()

        if not update_result:
            result.error = ErrorDetail(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User with this email not found",
            )
            return result

        result.detail = "User successfully updated"
        result.updated_user_id = update_result

    except IntegrityError:
        await db_session.rollback()
        result.error = ErrorDetail(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",

        )

    except Exception as error:
        await db_session.rollback()
        result.error = ErrorDetail(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Oops, something went wrong! {error}",
        )

    return result


async def get_users_with_accounts(
        page: int = Query(default=1),
        admin_session: UserSessionResponse = Depends(admin_info_session),
        db_session: AsyncSession = Depends(async_db_session)
) -> UsersWithAccountsResponse:
    result: UsersWithAccountsResponse = UsersWithAccountsResponse()

    try:
        if admin_session.error:
            result.error = ErrorDetail(
                status_code=admin_session.error.status_code,
                detail=admin_session.error.detail,
            )

        if page <= 0:
            result.error = ErrorDetail(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Page number must be greater than 0",
            )

            return result

        limit: int = USERS_PER_PAGE
        offset: int = (page - 1) * limit

        users_with_accounts: ScalarResult[Users] = await db_session.scalars(
            select(Users)
            .where(Users.is_active == 1)
            .options(selectinload(Users.accounts))
            .order_by(Users.id)
            .limit(limit)
            .offset(offset)
        )

        # Можно добавить обработку для max_page

        for user in users_with_accounts.all():
            result.users.append(  # type: ignore
                UserWithAccount(
                    id=user.id,
                    email=user.email,
                    role_id=user.role_id,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    created_at=user.created_at,
                    updated_at=user.updated_at,
                    accounts=[
                        UserAccount(
                            id=account.id,
                            name=account.name,
                            balance=account.balance,
                            created_at=account.created_at,
                            updated_at=account.updated_at,
                            is_active=account.is_active,
                        ) for account in user.accounts
                    ]
                )
            )

        result.page = page
        result.max_user_per_page = USERS_PER_PAGE
        # Можно добавить в модель различные атрибуты (max_page, next_page, prev_page и т.п)

    except Exception as error:
        result.error = ErrorDetail(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Oops, something went wrong! {error}",
        )

    return result
