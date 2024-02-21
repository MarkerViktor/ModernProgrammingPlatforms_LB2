from aiohttp import web
from pydantic import BaseModel

from src.entities import Role
from src.services.auth import AuthService, KnownLoginError, BadLoginCredentialsError
from src.services.users import UsersService
from src.utils import require, PydanticForm, Auth

router = web.RouteTableDef()


class SignInCredentials(BaseModel):
    login: str
    password: str


@router.post("/sign_in")
@require(
    payload=PydanticForm(SignInCredentials),
)
async def sign_in_handler(request: web.Request, payload: SignInCredentials) -> web.Response:
    try:
        result = await AuthService().login(payload.login, payload.password)
    except BadLoginCredentialsError:
        raise web.HTTPBadRequest(text="Неверный логин или пароль.")

    response = web.json_response(result)
    response.set_cookie(
        "X-Auth-Token",
        value=result.token,
        httponly=True,
    )

    return response


@router.post("/sign_out")
@require(Auth(Role.ADMIN, Role.USER))
async def sign_out_handler(request: web.Request) -> web.Response:
    response = web.HTTPOk()
    response.del_cookie("X-Auth-Token")
    return response


class SignUpRequest(BaseModel):
    first_name: str
    last_name: str
    login: str
    password: str


@router.post("/sign_up")
@require(
    Auth(Role.GUEST),
    payload=PydanticForm(SignUpRequest),
)
async def sign_up_handler(_, payload: SignUpRequest) -> web.Response:
    try:
        await UsersService().register_new(payload.first_name, payload.last_name, payload.login, payload.password)
    except KnownLoginError:
        raise web.HTTPBadRequest(text="Предоставленный логин занят.")

    return web.HTTPOk()
