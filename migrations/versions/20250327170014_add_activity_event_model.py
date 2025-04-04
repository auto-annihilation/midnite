"""add activity event model

Revision ID: b326cfee2eea
Revises:
Create Date: 2025-03-27 17:00:14.818871

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b326cfee2eea"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "activity_event",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "transaction_type",
            sa.Enum("DEPOSIT", "WITHDRAW", name="activityeventtypeenum"),
            nullable=False,
        ),
        sa.Column("amount", sa.Numeric(), nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("event_received_at", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("activity_event", schema=None) as batch_op:
        batch_op.create_index(
            "idx_events_created_by_user", ["user_id", "event_received_at"], unique=False
        )
        batch_op.create_index(
            batch_op.f("ix_activity_event_created_at"), ["created_at"], unique=False
        )
        batch_op.create_index(
            batch_op.f("ix_activity_event_event_received_at"),
            ["event_received_at"],
            unique=False,
        )
        batch_op.create_index(
            batch_op.f("ix_activity_event_updated_at"), ["updated_at"], unique=False
        )

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("activity_event", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_activity_event_updated_at"))
        batch_op.drop_index(batch_op.f("ix_activity_event_event_received_at"))
        batch_op.drop_index(batch_op.f("ix_activity_event_created_at"))
        batch_op.drop_index("idx_events_created_by_user")

    op.drop_table("activity_event")
    # ### end Alembic commands ###
