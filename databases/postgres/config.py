from os import getenv as os_getenv
from typing import Optional

from dotenv import load_dotenv, find_dotenv

from databases.postgres.dto import PostgresDTO

load_dotenv(find_dotenv(".env.test"))


class PostgreSQL:
    def __init__(self, psql_dto: PostgresDTO) -> None:
        self._HOST: str = psql_dto.HOST
        self._PORT: str = psql_dto.PORT
        self._USER: str = psql_dto.USER
        self._PASSWORD: Optional[str] = psql_dto.PASSWORD
        self._DATABASE: str = psql_dto.DATABASE

        self.DSN: str = self._generate_dsn()

    def _generate_dsn(self):
        return f"postgresql+psycopg://{self._USER}:{self._PASSWORD}@{self._HOST}:{self._PORT}/{self._DATABASE}"


postgres: PostgreSQL = PostgreSQL(
    PostgresDTO(
        HOST=os_getenv("POSTGRES_HOST", "localhost"),
        PORT=os_getenv("POSTGRES_PORT", "5432"),
        USER=os_getenv("POSTGRES_USER", "postgres"),
        PASSWORD=os_getenv("POSTGRES_PASSWORD", "postgres"),
        DATABASE=os_getenv("POSTGRES_DATABASE", "postgres")
    )
)
