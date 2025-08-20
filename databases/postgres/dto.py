from dataclasses import dataclass
from typing import Optional


@dataclass
class PostgresDTO:
    HOST: str
    PORT: str
    USER: str
    PASSWORD: Optional[str]
    DATABASE: str
