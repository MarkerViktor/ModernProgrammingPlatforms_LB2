from aiohttp import web

from src.services.auth import AuthResult, AuthService


@web.middleware
async def auth_middleware(request: web.Request, handler) -> web.StreamResponse:
    token = request.cookies.get("X-Auth-Token")
    if token is None:
        auth = AuthResult(is_authorized=False)
    else:
        auth = await AuthService().authorize(token)

    request["auth"] = auth
    return await handler(request)
