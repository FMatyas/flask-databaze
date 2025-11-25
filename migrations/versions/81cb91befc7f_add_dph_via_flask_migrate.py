"""add dph via flask-migrate

Revision ID: 81cb91befc7f
Revises: 
Create Date: 2025-10-09 09:09:08.462363

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '81cb91befc7f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Add column in a way that avoids batch_alter_table temporary table issues on SQLite
    op.add_column('product', sa.Column('dph', sa.Integer(), nullable=True, server_default=sa.text('15')))
    # Ensure existing rows have value
    op.execute("UPDATE product SET dph = 15 WHERE dph IS NULL")
    # Optionally remove server_default (keep column nullable to avoid complex SQLite ALTER)
    try:
        op.alter_column('product', 'dph', existing_type=sa.Integer(), server_default=None)
    except Exception:
        pass


def downgrade():
    op.drop_column('product', 'dph')
