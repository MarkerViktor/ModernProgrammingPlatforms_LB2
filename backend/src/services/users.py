from sqlalchemy import insert, exists

from src.entities import User, Role
from src.services.auth import AuthService, KnownLoginError
from src.services.base import BaseService
from src.tables import users


class UsersService(BaseService):
    async def register_new(self, first_name: str, last_name: str, login: str, password: str) -> None:
        user = await self.create_user(first_name, last_name, Role.USER)
        try:
            await AuthService().create_credentials(user.id, login, password)
        except KnownLoginError:
            raise

    async def create_user(self, first_name: str, last_name: str, role: Role) -> User:
        user_id = await self._db_conn.scalar(
            insert(users)
            .values(
                first_name=first_name,
                last_name=last_name,
                role=role,
            )
            .returning(users.c.id)
        )
        return User(user_id, first_name, last_name, role)

    async def check_user_exists(self, user_id: int) -> bool:
        return await self._db_conn.scalar(exists().where(users.c.id == user_id).select())


class UnknownUserError(Exception):
    ...
