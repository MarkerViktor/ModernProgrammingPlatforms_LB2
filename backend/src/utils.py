import abc
import asyncio
import functools
import logging
import typing

from PIL import Image, UnidentifiedImageError
from aiohttp import web
from pydantic import BaseModel, ValidationError

from src.entities import Role
from src.services.auth import AuthResult


class Checker(abc.ABC):
    @abc.abstractmethod
    async def __call__(self, request: web.Request) -> None:
        ...


class Requirement(Checker):
    @abc.abstractmethod
    async def __call__(self, request: web.Request) -> typing.Any:
        ...


Handler = typing.Callable[[web.Request], typing.Awaitable[web.StreamResponse]]
HandlerWithRequirements = typing.Callable[[web.Request, ...], typing.Awaitable[web.StreamResponse]]


class require:
    def __init__(self, *checkers: Checker, **requirements: Requirement):
        self._checkers = checkers
        self._requirements = requirements

    def __call__(self, handler: HandlerWithRequirements) -> Handler:
        @functools.wraps(handler)
        async def wrapper(request: web.Request):
            # To avoid body reading race in requirements
            await request.post()

            checkers_coroutines = (checker(request) for checker in self._checkers)
            requirements_coroutines = (requirement(request) for requirement in self._requirements.values())

            checkers, requirements_values = await asyncio.gather(
                asyncio.gather(*checkers_coroutines),
                asyncio.gather(*requirements_coroutines),
            )

            requirements = dict(zip(self._requirements.keys(), requirements_values))
            return await handler(request, **requirements)

        return wrapper


class PydanticJSON(Requirement):
    def __init__(self, model: typing.Type[BaseModel]):
        self._model = model

    async def __call__(self, request: web.Request) -> BaseModel:
        if request.content_type != "application/json":
            raise web.HTTPBadRequest(
                text="Only application/json Content-Type accepted.",
            )

        body = await request.text()
        try:
            payload = self._model.parse_raw(body)
        except ValidationError as e:
            raise web.HTTPBadRequest(text=e.json())
        return payload


class PydanticQuery(Requirement):
    def __init__(self, model: typing.Type[BaseModel]):
        self._model = model

    async def __call__(self, request: web.Request) -> BaseModel:
        query = request.query

        params = {}
        for key in query.keys():
            values = query.getall(key)
            params[key] = values if len(values) > 1 else values[0]

        try:
            payload = self._model.parse_obj(query)
        except ValidationError as e:
            raise web.HTTPBadRequest(text=e.json())
        return payload


class PydanticForm(Requirement):
    def __init__(self, model: typing.Type[BaseModel]):
        self._model = model

    async def __call__(self, request: web.Request) -> typing.Any:
        if request.content_type not in {"application/x-www-form-urlencoded", "multipart/form-data"}:
            raise web.HTTPBadRequest(
                text="Only application/x-www-form-urlencoded or multipart/form-data Content-Types accepted."
            )

        form_data = await request.post()
        fields = {}
        for key in form_data.keys():
            values = form_data.getall(key)
            fields[key] = values if len(values) > 1 else values[0]

        try:
            payload = self._model.parse_obj(fields)
        except ValidationError as e:
            raise web.HTTPBadRequest(text=e.json())
        return payload


class FormField(Requirement):
    def __init__(self, field_name: str, type_: type):
        self._field_name = field_name
        self._type = type_

    async def __call__(self, request: web.Request) -> typing.Any:
        if request.content_type not in {"multipart/form-data", "application/x-www-form-urlencoded"}:
            raise web.HTTPBadRequest(
                text="Only multipart/form-data or application/x-www-form-urlencoded Content-Types accepted."
            )

        post_data = await request.post()

        field = post_data.get(self._field_name)
        if field is None:
            raise web.HTTPBadRequest(text=f'Form-data field "{self._field_name}" is required.')

        if self._type is Image.Image:
            if not isinstance(field, web.FileField):
                raise web.HTTPBadRequest(text=f'From-data field "{self._field_name}" doesn\'t contain file.')
            try:
                image = Image.open(field.file)
            except UnidentifiedImageError:
                return web.HTTPBadRequest(text="Cannot identify image file. It's invalid.")
            return image

        try:
            value = self._type(field)
        except (ValueError, TypeError):
            raise web.HTTPBadRequest(text=f'Can\'t cast field "{self._field_name}" to required type {self._type}.')
        return value


_AUTH_LOGGER = logging.getLogger("auth")


class Auth(Requirement):
    def __init__(self, *allowed_roles: Role):
        self._allowed_roles = allowed_roles

    async def __call__(self, request: web.Request) -> typing.Any:
        auth: AuthResult = request["auth"]

        _AUTH_LOGGER.info(f"User {auth.user_id} authorized with role {auth.role}.")

        if len(self._allowed_roles) != 0 and auth.role not in self._allowed_roles:
            raise web.HTTPForbidden()

        return auth
