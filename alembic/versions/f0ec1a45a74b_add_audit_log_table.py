"""add audit_log table

Revision ID: f0ec1a45a74b
Revises: a4a89e3c7f24
Create Date: 2026-05-30 08:31:24.028447

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f0ec1a45a74b'
down_revision: Union[str, None] = 'a4a89e3c7f24'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Антон: створюємо таблицю audit_log вручну — Alembic не підхопив модель автоматично
    op.create_table(
        'audit_log',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('username', sa.String(length=50), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=False),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.Column('resource', sa.String(length=100), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('http_method', sa.String(length=10), nullable=True),
        sa.Column('endpoint', sa.String(length=200), nullable=True),
        sa.Column('status_code', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('details', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    # Богдан: індекси для швидкого пошуку
    op.create_index('ix_audit_log_id', 'audit_log', ['id'], unique=False)
    op.create_index('ix_audit_log_timestamp', 'audit_log', ['timestamp'], unique=False)
    op.create_index('ix_audit_action_ts', 'audit_log', ['action', 'timestamp'], unique=False)
    op.create_index('ix_audit_user_ts', 'audit_log', ['user_id', 'timestamp'], unique=False)
    op.create_index('ix_audit_ip_action', 'audit_log', ['ip_address', 'action'], unique=False)

    # Влад: зміни у таблиці users з попередньої міграції
    op.add_column('users', sa.Column('encrypted_email', sa.String(), nullable=True))
    op.add_column('users', sa.Column('encrypted_phone', sa.String(), nullable=True))
    op.add_column('users', sa.Column('full_name', sa.String(), nullable=True))
    op.add_column('users', sa.Column('created_at', sa.DateTime(), nullable=True))
    op.drop_column('users', 'email')


def downgrade() -> None:
    op.drop_index('ix_audit_ip_action', table_name='audit_log')
    op.drop_index('ix_audit_user_ts', table_name='audit_log')
    op.drop_index('ix_audit_action_ts', table_name='audit_log')
    op.drop_index('ix_audit_log_timestamp', table_name='audit_log')
    op.drop_index('ix_audit_log_id', table_name='audit_log')
    op.drop_table('audit_log')

    op.add_column('users', sa.Column('email', sa.VARCHAR(), nullable=True))
    op.drop_column('users', 'created_at')
    op.drop_column('users', 'full_name')
    op.drop_column('users', 'encrypted_phone')
    op.drop_column('users', 'encrypted_email')
