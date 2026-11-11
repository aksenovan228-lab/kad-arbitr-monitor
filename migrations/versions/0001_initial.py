from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("telegram_id", sa.BigInteger(), nullable=False),
        sa.Column("timezone", sa.String(64), nullable=False, server_default="Europe/Moscow"),
        sa.Column("consent_version", sa.String(32), nullable=True),
        sa.Column("consented_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_users_telegram_id", "users", ["telegram_id"], unique=True)
    op.create_table(
        "tracked_inns",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("inn", sa.String(12), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("user_id", "inn", name="uq_tracked_inns_user_inn"),
    )
    op.create_index("ix_tracked_inns_user_id", "tracked_inns", ["user_id"])
    op.create_index("ix_tracked_inns_inn", "tracked_inns", ["inn"])


def downgrade():
    op.drop_index("ix_tracked_inns_inn", table_name="tracked_inns")
    op.drop_index("ix_tracked_inns_user_id", table_name="tracked_inns")
    op.drop_table("tracked_inns")
    op.drop_index("ix_users_telegram_id", table_name="users")
    op.drop_table("users")
