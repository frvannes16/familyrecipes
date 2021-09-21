"""Create the users and recipes tables.

Revision ID: 782ff7860ac6
Revises: 
Create Date: 2021-09-21 14:58:10.455706

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "782ff7860ac6"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("first_name", sa.String(), nullable=True),
        sa.Column("last_name", sa.String(), nullable=True),
        sa.Column("email", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)
    op.create_table(
        "recipes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("steps", sa.String(), nullable=True),
        sa.Column("author_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(
            ["author_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_recipes_author_id"), "recipes", ["author_id"], unique=False
    )
    op.create_index(op.f("ix_recipes_id"), "recipes", ["id"], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_recipes_id"), table_name="recipes")
    op.drop_index(op.f("ix_recipes_author_id"), table_name="recipes")
    op.drop_table("recipes")
    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_table("users")
    # ### end Alembic commands ###