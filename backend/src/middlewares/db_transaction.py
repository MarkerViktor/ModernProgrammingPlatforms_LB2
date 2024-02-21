import contextvars

from aiohttp import web
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine

_DB_CONN: contextvars.ContextVar[AsyncConnection] = contextvars.ContextVar("db_conn")


def get_db_conn() -> AsyncConnection:
    return _DB_CONN.get()


@web.middleware
async def request_transaction_middleware(request: web.Request, handler) -> web.StreamResponse:
    engine: AsyncEngine = request.app["db_engine"]

    conn = engine.connect()
    await conn.start()

    _DB_CONN.set(conn)

    try:
        try:
            response = await handler(request)
        except Exception:
            await conn.rollback()
            raise
        else:
            await conn.commit()

        return response
    finally:
        await conn.close()
