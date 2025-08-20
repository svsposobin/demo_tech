from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

from src.utils import hash_password

revision: str = '592c2bfc2ad5'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('roles',
                    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
                    sa.Column('name', sa.String(length=20), nullable=False),
                    sa.CheckConstraint("name IN ('user', 'admin')", name='chk_role_name'),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('name')
                    )
    op.create_table('users',
                    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
                    sa.Column('role_id', sa.Integer(), nullable=True),
                    sa.Column('email', sa.String(length=255), nullable=False),
                    sa.Column('first_name', sa.String(length=100), nullable=False),
                    sa.Column('last_name', sa.String(length=100), nullable=True),
                    sa.Column('hash_password', sa.LargeBinary(), nullable=False),
                    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False,
                              comment='Дата регистрации в UTC'),
                    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'),
                              nullable=False),
                    sa.Column('is_active', sa.SmallInteger(), nullable=False),
                    sa.CheckConstraint('is_active IN (0, 1)', name='chk_user_is_active'),
                    sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('email')
                    )
    op.create_table('accounts',
                    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
                    sa.Column('user_id', sa.Integer(), nullable=False),
                    sa.Column('name', sa.String(length=100), nullable=False),
                    sa.Column('balance', sa.Numeric(precision=15, scale=2), nullable=False),
                    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False,
                              comment='Дата создания счета в UTC'),
                    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'),
                              nullable=False),
                    sa.Column('is_active', sa.SmallInteger(), nullable=False),
                    sa.CheckConstraint('is_active IN (0, 1)', name='chk_account_is_active'),
                    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('users_sessions',
                    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
                    sa.Column('session_token', sa.String(length=100), nullable=False),
                    sa.Column('user_id', sa.Integer(), nullable=False),
                    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'),
                              nullable=False),
                    sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
                    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('transactions',
                    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
                    sa.Column('account_id', sa.Integer(), nullable=False),
                    sa.Column('type', sa.String(length=10), nullable=False),
                    sa.Column('amount', sa.Numeric(precision=15, scale=2), nullable=False),
                    sa.Column('status', sa.String(length=20), nullable=False),
                    sa.Column('external_id', sa.String(length=100), nullable=True,
                              comment='ID транзакции во внешней системе (банк, платежный шлюз и т.д.)'),
                    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'),
                              nullable=False),
                    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'),
                              nullable=False),
                    sa.CheckConstraint("status IN ('pending', 'completed', 'failed', 'cancelled')",
                                       name='chk_transaction_status'),
                    sa.CheckConstraint("type IN ('debit', 'credit')", name='chk_transaction_type'),
                    sa.ForeignKeyConstraint(['account_id'], ['accounts.id'], ),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('external_id')
                    )
    connection = op.get_bind()

    op.execute("INSERT INTO roles (id, name) VALUES (1, 'user'), (2, 'admin')")

    hash_admin_password: bytes = hash_password(password="admin")
    connection.execute(
        statement=text(
            """
            INSERT INTO users (role_id, email, first_name, last_name, hash_password, is_active)
            VALUES (:role_id, :email, :first_name, :last_name, :hash_password, :is_active)
            """
        ),
        parameters={
            'role_id': 2,
            'email': 'admin@admin.admin',
            'first_name': 'admin',
            'last_name': None,
            'hash_password': hash_admin_password,
            'is_active': 1
        }
    )

    hash_user_password: bytes = hash_password(password="user")
    test_users = [
        {
            'role_id': 1,
            'email': 'test_user1@user.user',
            'first_name': 'Alex',
            'last_name': 'Smith',
            'hash_password': hash_user_password,
            'is_active': 1
        },
        {
            'role_id': 1,
            'email': 'test_user2@user.user',
            'first_name': 'John',
            'last_name': None,
            'hash_password': hash_user_password,
            'is_active': 1
        },
        {
            'role_id': 1,
            'email': 'test_user3@user.user',
            'first_name': 'Anna',
            'last_name': 'Smith',
            'hash_password': hash_user_password,
            'is_active': 1
        },
        {
            'role_id': 1,
            'email': 'test_user4@user.user',
            'first_name': 'Julia',
            'last_name': None,
            'hash_password': hash_user_password,
            'is_active': 1
        }
    ]
    connection.execute(
        statement=text(
            """
                INSERT INTO users (role_id, email, first_name, last_name, hash_password, is_active)
                VALUES (:role_id, :email, :first_name, :last_name, :hash_password, :is_active)
            """
        ),
        parameters=test_users
    )

    test_accounts = [
        {
            "user_id": 1,
            "name": "main_admin_account",
            "balance": 500,
            "is_active": 1
        },
        {
            "user_id": 1,
            "name": "second_admin_account",
            "balance": 0,
            "is_active": 1
        },
        {
            "user_id": 2,
            "name": "main_user1_account",
            "balance": 1000,
            "is_active": 1
        },
        {
            "user_id": 3,
            "name": "main_user2_account",
            "balance": 250,
            "is_active": 1
        }
    ]
    connection.execute(
        statement=text(
            """
                INSERT INTO accounts (user_id, name, balance, is_active)
                VALUES (:user_id, :name, :balance, :is_active)
            """
        ),
        parameters=test_accounts
    )

    test_transactions = [
        {
            "account_id": 1,
            "type": "debit",
            "amount": 500,
            "status": "completed",
            "external_id": "FSwr1r2tafk12j1kgg543g"
        },
        {
            "account_id": 1,
            "type": "debit",
            "amount": 200,
            "status": "cancelled",
            "external_id": "FDSAfewf32fwg54yudhdfhd43"
        },
        {
            "account_id": 3,
            "type": "debit",
            "amount": 500,
            "status": "pending",
            "external_id": "asfaewqgsdg2tgafGFR32fsdg4"
        }
    ]
    connection.execute(
        statement=text(
            """
                INSERT INTO transactions (account_id, type, amount, status, external_id)
                VALUES (:account_id, :type, :amount, :status, :external_id)
            """
        ),
        parameters=test_transactions
    )


def downgrade() -> None:
    op.drop_table('transactions')
    op.drop_table('users_sessions')
    op.drop_table('accounts')
    op.drop_table('users')
    op.drop_table('roles')
