import hashlib
import uuid
from dataclasses import dataclass

from sqlalchemy import select, delete, exists
from sqlalchemy.dialects.postgresql import insert

from src import config
from src.entities import Role
from src.services.base import BaseService
from src.tables import user_credentials, user_tokens, users


def calculate_hash(password: str) -> bytes:
    return hashlib.pbkdf2_hmac(
        hash_name="sha256",
        password=password.encode("utf-8"),
        salt=config.PASSWORD_HASH_SALT,
        iterations=config.PASSWORD_HASH_ITERATIONS,
        dklen=config.PASSWORD_HASH_LENGTH,
    )


def generate_token() -> str:
    return str(uuid.uuid4())


class AuthService(BaseService):
    async def login(self, login: str, password: str) -> "LoginResult":
        user_record = (
            await self._db_conn.execute(
                select(user_credentials.c.user_id, users.c.role)
                .join(users)
                .where(user_credentials.c.login == login)
                .where(user_credentials.c.password_hash == calculate_hash(password))
            )
        ).first()

        if user_record is None:
            raise BadLoginCredentialsError("Неверные логин или пароль.")
        user_id, role = user_record

        token = generate_token()
        await self._db_conn.execute(
            insert(user_tokens)
            .values(user_id=user_id, token=token)
            .on_conflict_do_update(
                constraint=user_tokens.primary_key,
                set_={user_tokens.c.token: token},
            )
        )

        return LoginResult(token, role, user_id)

    async def authorize(self, token: str) -> "AuthResult":
        user_record = (
            await self._db_conn.execute(
                select(users.c.id, users.c.role).join(user_tokens).where(user_tokens.c.token == token)
            )
        ).first()

        if user_record is None:
            return AuthResult(is_authorized=False)

        user_id, role = user_record
        return AuthResult(
            is_authorized=True,
            role=Role(role.lower()),
            user_id=user_id,
        )

    async def logout(self, token: str) -> None:
        auth = await self.authorize(token)

        if not auth.is_authorized:
            raise UnknownTokenError("Неизвестный токен авторизации.")

        await self._db_conn.execute(delete(user_tokens).where(user_tokens.c.token == token))

    async def create_credentials(self, user_id: int, login: str, password: str) -> None:
        is_exists = await self._db_conn.scalar(select(exists().where(user_credentials.c.login == login)))
        if is_exists:
            raise KnownLoginError(f'Логин "{login}" уже занят.')

        await self._db_conn.execute(
            insert(user_credentials).values(
                user_id=user_id,
                login=login,
                password_hash=calculate_hash(password),
            )
        )


@dataclass
class LoginResult:
    token: str
    role: Role
    user_id: int


@dataclass
class AuthResult:
    is_authorized: bool
    role: Role = Role.GUEST
    user_id: int | None = None


class UnknownTokenError(Exception):
    ...


class KnownLoginError(Exception):
    ...


class BadLoginCredentialsError(Exception):
    ...
