import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncEngine

from src.entities import Role, RateKind

metadata = sa.MetaData()

users = sa.Table(
    "users",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
    sa.Column("role", sa.Enum(Role), nullable=False, default=Role.GUEST),
    sa.Column("first_name", sa.Text, nullable=False),
    sa.Column("last_name", sa.Text, nullable=False),
)

user_credentials = sa.Table(
    "user_credentials",
    metadata,
    sa.Column("user_id", sa.Integer, sa.ForeignKey(users.c.id), primary_key=True),
    sa.Column("login", sa.Text, nullable=False, unique=True),
    sa.Column("password_hash", sa.LargeBinary, nullable=False),
)

user_tokens = sa.Table(
    "user_auth",
    metadata,
    sa.Column("user_id", sa.Integer, sa.ForeignKey(users.c.id), primary_key=True),
    sa.Column("token", sa.Text, unique=True),
)

posts = sa.Table(
    "posts",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
    sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    sa.Column("text", sa.Text, nullable=False),
    sa.Column("image_url", sa.Text, nullable=False),
    sa.Column("likes_quantity", sa.Integer, nullable=False, server_default="0"),
    sa.Column("dislikes_quantity", sa.Integer, nullable=False, server_default="0"),
)

post_rates = sa.Table(
    "post_rates",
    metadata,
    sa.Column("post_id", sa.Integer, sa.ForeignKey(posts.c.id, ondelete="CASCADE"), primary_key=True),
    sa.Column("user_id", sa.Integer, sa.ForeignKey(users.c.id, ondelete="CASCADE"), primary_key=True),
    sa.Column("rate", sa.Enum(RateKind), nullable=False),
)


async def create_schema(engine: AsyncEngine) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)
