import functools
import json

from aiohttp import web
from aiohttp_middlewares import cors_middleware
from pydantic.json import pydantic_encoder
from sqlalchemy.ext.asyncio import create_async_engine

from src import config
from src.controllers.auth import router as auth_router
from src.controllers.posts import router as posts_router
from src.tables import create_schema
from src.middlewares.auth import auth_middleware
from src.middlewares.db_transaction import request_transaction_middleware


async def init_database(app: web.Application) -> None:
    db_url = config.DB_URL.replace("postgresql:/", "postgresql+asyncpg:/").replace("sqlite:/", "sqlite+aiosqlite:/")
    engine = create_async_engine(db_url, echo=True)
    await create_schema(engine)
    app["db_engine"] = engine
    yield
    await engine.dispose()


# Setup json serializer for responses
web.json_response = functools.partial(
    web.json_response,
    dumps=functools.partial(
        json.dumps,
        default=pydantic_encoder,
    ),
)


def init() -> web.Application:
    app = web.Application(
        middlewares=[
            cors_middleware(allow_all=True, allow_credentials=True),
            request_transaction_middleware,
            auth_middleware,
        ],
        client_max_size=1024**2 * 20,  # 20MB
    )
    app.cleanup_ctx.append(init_database)

    app.add_routes(auth_router)
    app.add_routes(posts_router)

    return app


if __name__ == "__main__":
    import logging

    logging.basicConfig(level=logging.INFO)
    web.run_app(init(), port=8080)
