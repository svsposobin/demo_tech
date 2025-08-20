from sqlalchemy import (
    String,
    DateTime,
    ForeignKey,
    Numeric,
    CheckConstraint,
    SmallInteger,
    LargeBinary
)
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship
from sqlalchemy.sql import func
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from typing import Optional, List

from src.sso.core.constants import COOKIE_SESSION_EXPIRE_MINUTES


class BaseMeta(DeclarativeBase):
    pass


class Users(BaseMeta):
    __tablename__: str = "users"
    __table_args__ = (
        CheckConstraint("is_active IN (0, 1)", name="chk_user_is_active"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), nullable=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    hash_password: Mapped[bytes] = mapped_column(LargeBinary(), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        comment="Дата регистрации в UTC"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
    is_active: Mapped[int] = mapped_column(SmallInteger, default=1, nullable=False)

    # Relationships
    role: Mapped[Optional["Roles"]] = relationship("Roles", back_populates="users")
    accounts: Mapped[List["Accounts"]] = relationship("Accounts", back_populates="user")
    sessions: Mapped[List["UsersSessions"]] = relationship("UsersSessions", back_populates="user")

    def __repr__(self):
        return f"<Users(id={self.id}, email={self.email})>"


class Roles(BaseMeta):
    __tablename__: str = "roles"
    __table_args__ = (
        CheckConstraint("name IN ('user', 'admin')", name="chk_role_name"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)

    # Relationships
    users: Mapped[List["Users"]] = relationship("Users", back_populates="role")

    def __repr__(self):
        return f"<Roles(id={self.id}, name={self.name})>"


class Accounts(BaseMeta):
    __tablename__: str = "accounts"
    __table_args__ = (
        CheckConstraint("is_active IN (0, 1)", name="chk_account_is_active"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    balance: Mapped[Decimal] = mapped_column(
        Numeric(precision=15, scale=2),
        default=Decimal('0.00'),
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        comment="Дата создания счета в UTC"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
    is_active: Mapped[int] = mapped_column(SmallInteger, default=1, nullable=False)

    # Relationships
    user: Mapped["Users"] = relationship("Users", back_populates="accounts")
    transactions: Mapped[List["Transactions"]] = relationship("Transactions", back_populates="account")

    def __repr__(self):
        return f"<Accounts(id={self.id}, user_id={self.user_id}, balance={self.balance})>"


class Transactions(BaseMeta):
    __tablename__: str = "transactions"
    __table_args__ = (
        CheckConstraint("type IN ('debit', 'credit')", name="chk_transaction_type"),
        CheckConstraint("status IN ('pending', 'completed', 'failed', 'cancelled')", name="chk_transaction_status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"), nullable=False)
    type: Mapped[str] = mapped_column(String(10), nullable=False)
    amount: Mapped[Decimal] = mapped_column(
        Numeric(precision=15, scale=2),
        nullable=False
    )
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)
    external_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        unique=True,
        comment="ID транзакции во внешней системе (банк, платежный шлюз и т.д.)"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Relationships
    account: Mapped["Accounts"] = relationship("Accounts", back_populates="transactions")

    def __repr__(self):
        return f"<Transactions(id={self.id}, account_id={self.account_id}, type={self.type}, amount={self.amount})>"


class UsersSessions(BaseMeta):
    __tablename__: str = "users_sessions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    session_token: Mapped[str] = mapped_column(String(100), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    # Relationships
    user: Mapped["Users"] = relationship("Users", back_populates="sessions")

    @classmethod
    def create_with_lifetime(
            cls,
            user_id: int,
            session_token: str,
            minutes: int = COOKIE_SESSION_EXPIRE_MINUTES
    ) -> "UsersSessions":
        """Сессия с кастомным временем жизни"""
        now: datetime = datetime.now(timezone.utc).replace(tzinfo=None)
        instance: UsersSessions = cls()

        instance.user_id = user_id
        instance.session_token = session_token
        instance.expires_at = now + timedelta(minutes=minutes)

        return instance
