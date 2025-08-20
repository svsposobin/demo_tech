from contextlib import asynccontextmanager
from typing import AsyncGenerator, Any

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, async_sessionmaker

from databases.postgres.config import postgres
from src.constants import (
    POSTGRES_POOL_SIZE,
    POSTGRES_MAX_OVERFLOW,
    POSTGRES_POOL_TIMEOUT,
    POSTGRES_POOL_RECYCLE
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, Any]:
    engine: AsyncEngine = create_async_engine(
        url=postgres.DSN,
        pool_size=POSTGRES_POOL_SIZE,
        max_overflow=POSTGRES_MAX_OVERFLOW,
        pool_timeout=POSTGRES_POOL_TIMEOUT,
        pool_recycle=POSTGRES_POOL_RECYCLE,
        echo=False,
    )

    app.state.session_factory = async_sessionmaker(engine)

    yield

    await engine.dispose()
