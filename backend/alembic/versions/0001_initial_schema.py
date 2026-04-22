"""Initial schema: users and contract_analyses tables

Revision ID: 0001
Revises:
Create Date: 2024-01-01 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create custom enum types
    analysis_status = postgresql.ENUM(
        "pending", "processing", "completed", "failed", name="analysis_status"
    )
    risk_level = postgresql.ENUM("low", "medium", "high", name="risk_level")
    analysis_status.create(op.get_bind(), checkfirst=True)
    risk_level.create(op.get_bind(), checkfirst=True)

    # users table
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("hashed_password", sa.String(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("free_analyses_used", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("stripe_customer_id", sa.String(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)

    # contract_analyses table
    op.create_table(
        "contract_analyses",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("filename", sa.String(), nullable=False),
        sa.Column("file_url", sa.String(), nullable=True),
        sa.Column(
            "status",
            sa.Enum("pending", "processing", "completed", "failed", name="analysis_status"),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("overall_risk_score", sa.Float(), nullable=True),
        sa.Column(
            "overall_risk_level",
            sa.Enum("low", "medium", "high", name="risk_level"),
            nullable=True,
        ),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("clauses", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index(
        op.f("ix_contract_analyses_user_id"),
        "contract_analyses",
        ["user_id"],
    )


def downgrade() -> None:
    op.drop_table("contract_analyses")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")

    op.execute("DROP TYPE IF EXISTS analysis_status")
    op.execute("DROP TYPE IF EXISTS risk_level")
