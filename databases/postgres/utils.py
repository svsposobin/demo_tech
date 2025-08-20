from typing import AsyncGenerator

from fastapi.requests import Request
from sqlalchemy.ext.asyncio import AsyncSession


async def async_db_session(request: Request) -> AsyncGenerator[AsyncSession, None]:
    async with request.app.state.session_factory() as session:
        yield session
