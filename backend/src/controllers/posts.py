import math
from dataclasses import dataclass

from PIL.Image import Image
from aiohttp import web
from pydantic import BaseModel, Field

from src.entities import Role, RateKind, Post
from src.services.auth import AuthResult
from src.services.posts import PostsService, BadPostImageError, UnknownPostError, PostsSorter
from src.utils import require, Auth, PydanticQuery, FormField, PydanticJSON

router = web.RouteTableDef()


class GetPostsListRequest(BaseModel):
    page: int = Field(gt=0, default=1)
    per_page: int = Field(gt=0, default=5)
    order: PostsSorter = PostsSorter.NEW_FIRST

@dataclass
class PaginatedList:
    items: list
    total_quantity: int

@dataclass
class RatedPost(Post):
    rate: RateKind | None

@router.get('/posts')
@require(
    auth=Auth(Role.USER, Role.ADMIN),
    query=PydanticQuery(GetPostsListRequest),
)
async def get_posts(_, query: GetPostsListRequest, auth: AuthResult) -> web.Response:
    service = PostsService()
    posts = await service.get_list(
        limit=query.per_page,
        offset=(query.page - 1) * query.per_page,
        order=query.order,
    )
    user_rates = await service.get_rates(
        user_id=auth.user_id,
        *(p.id for p in posts)
    )
    rated_posts = [
        RatedPost(
            id=post.id,
            created_at=post.created_at,
            text=post.text,
            image_url=post.image_url,
            likes_quantity=post.likes_quantity,
            dislikes_quantity=post.dislikes_quantity,
            rate=user_rates.get(post.id),
        )
        for post in posts
    ]
    total_quantity = await service.get_total_quantity()

    return web.json_response(
        PaginatedList(
            items=rated_posts,
            total_quantity=total_quantity,
        )
    )


@router.post('/posts')
@require(
    Auth(Role.ADMIN),
    post_text=FormField('text', str),
    post_image=FormField('image', Image),
)
async def create_new_post(_, post_text: str, post_image: Image) -> web.Response:
    try:
        post = await PostsService()\
            .create_post(
                text=post_text,
                image=post_image,
            )
    except BadPostImageError:
        raise web.HTTPBadRequest(text='Неверный формат изображения поста.')

    return web.json_response(post)


class SetPostReactionRequest(BaseModel):
    rate: RateKind | None

@router.put(r'/posts/{post_id:\d+}/rate')
@require(
    auth=Auth(Role.USER),
    payload=PydanticJSON(SetPostReactionRequest),
)
async def set_post_rate(request: web.Request, auth: AuthResult, payload: SetPostReactionRequest) -> web.Response:
    post_id = int(request.match_info['post_id'])
    try:
        await PostsService().update_user_rate(post_id, auth.user_id, payload.rate)
    except UnknownPostError:
        raise web.HTTPNotFound(text='Неизвестный идентификатор поста.')
    return web.HTTPOk()


@router.delete(r'/posts/{post_id:\d+}')
@require(
    Auth(Role.ADMIN),
)
async def delete_post(request: web.Request) -> web.Response:
    post_id = int(request.match_info['post_id'])
    try:
        await PostsService().delete_post(post_id)
    except UnknownPostError:
        raise web.HTTPNotFound(text='Неизвестный идентификатор поста.')
    return web.HTTPOk()
