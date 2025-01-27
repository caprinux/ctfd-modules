"""Add column to challenges
"""
import sqlalchemy as sa
from CTFd.plugins.migrations import get_columns_for_table

revision = "60a8b7fcc651"
down_revision = None
branch_labels = None
depends_on = None

def upgrade(op=None):
    columns = get_columns_for_table(
        op=op, table_name="challenges", names_only=True
    )
    if "module" not in columns:
        op.add_column(
            "challenges",
            sa.Column("module", sa.String(length=80)),
        )
    conn = op.get_bind()
    url = str(conn.engine.url)
    if url.startswith("postgres"):
        conn.execute(
            "UPDATE challenges SET module = 'uncategorized' WHERE module IS NULL"
        )
    else:
        conn.execute(
            "UPDATE challenges SET `module` = 'uncategorized' WHERE `module` IS NULL"
        )


def downgrade(op=None):
    columns = get_columns_for_table(
        op=op, table_name="challenges", names_only=True
    )
    if "module" in columns:
        op.drop_column("challenges", "module")
