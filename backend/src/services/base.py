from sqlalchemy.ext.asyncio import AsyncConnection

from src.middlewares.db_transaction import get_db_conn


class BaseService:
    @property
    def _db_conn(self) -> AsyncConnection:
        return get_db_conn()
