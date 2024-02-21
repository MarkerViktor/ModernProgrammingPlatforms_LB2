import enum

from PIL.Image import Image
from sqlalchemy import select, update, delete, exists
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.sql.functions import count

from src.entities import Post, RateKind, PostRate
from src.image_storage import ImageStorage
from src.services.base import BaseService
from src.services.users import UnknownUserError
from src.tables import posts, post_rates, users


def record_to_post(r) -> Post:
    return Post(
        id=r._mapping["id"],
        created_at=r._mapping["created_at"],
        text=r._mapping["text"],
        image_url=r._mapping["image_url"],
        likes_quantity=r._mapping["likes_quantity"],
        dislikes_quantity=r._mapping["dislikes_quantity"],
    )


def record_to_post_rate(r) -> PostRate:
    return PostRate(
        id=r._mapping["id"],
        post_id=r._mapping["post_id"],
        user_id=r._mapping["user_id"],
        rate=RateKind(r._mapping["rate"].lower()),
    )


def prepare_image(image: Image) -> Image:
    return image


class PostsSorter(str, enum.Enum):
    MORE_LIKES_FIRST = "more_likes_first"
    MODE_DISLIKES_FIRST = "more_dislikes_first"
    NEW_FIRST = "new_first"


class PostsService(BaseService):
    async def get_list(self, limit: int, offset: int, order: PostsSorter) -> list[Post]:
        if order == PostsSorter.NEW_FIRST:
            order_by = posts.c.created_at.desc()
        elif order == PostsSorter.MORE_LIKES_FIRST:
            order_by = posts.c.likes_quantity.desc()
        else:
            order_by = posts.c.dislikes_quantity.desc()

        stmt = select(posts).order_by(order_by).limit(limit).offset(offset)
        records = (await self._db_conn.execute(stmt)).all()
        return [record_to_post(r) for r in records]

    async def get_total_quantity(self) -> int:
        return await self._db_conn.scalar(select(count(posts.c.id)))

    async def get_rates(self, *posts_ids: int, user_id: int) -> dict[int, RateKind]:
        stmt = select(post_rates.c.post_id, post_rates.c.rate).join(users).join(posts).where(users.c.id == user_id)

        if posts_ids:
            stmt = stmt.where(posts.c.id.in_(posts_ids))

        records = (await self._db_conn.execute(stmt)).all()
        return {post_id: RateKind(rate.lower()) for post_id, rate in records}

    async def create_post(self, text: str, image: Image) -> Post:
        image = prepare_image(image)
        image_url = await ImageStorage.save(image)
        post_record = (
            await self._db_conn.execute(
                insert(posts)
                .values(
                    text=text,
                    image_url=image_url,
                )
                .returning(
                    posts.c.id,
                    posts.c.created_at,
                )
            )
        ).first()
        id_, created_at = post_record
        return Post(
            id=id_,
            created_at=created_at,
            text=text,
            image_url=image_url,
            likes_quantity=0,
            dislikes_quantity=0,
        )

    async def delete_post(self, post_id: int) -> None:
        if not await self._check_post_exists(post_id):
            raise UnknownPostError(f"Пост с идентификатором id={post_id} не существует.")

        await self._db_conn.execute(delete(posts).where(posts.c.id == post_id))

    async def _check_post_exists(self, post_id: int) -> bool:
        return await self._db_conn.scalar(exists().where(posts.c.id == post_id).select())

    async def update_user_rate(self, post_id: int, user_id: int, new_rate: RateKind | None) -> None:
        if not await self._check_post_exists(post_id):
            raise UnknownPostError(f"Пост с идентификатором id={post_id} не существует.")

        old_rate = await self._db_conn.scalar(
            select(post_rates.c.rate).where(post_rates.c.post_id == post_id).where(post_rates.c.user_id == user_id)
        )

        if old_rate == new_rate:
            # Rate not changed
            return

        # Post rates counters deltas
        likes, dislikes = 0, 0

        if old_rate == RateKind.LIKE:
            likes -= 1
        elif old_rate == RateKind.DISLIKE:
            dislikes -= 1

        if new_rate == RateKind.LIKE:
            likes += 1
        elif new_rate == RateKind.DISLIKE:
            dislikes += 1

        # Update post rates counters
        await self._db_conn.execute(
            update(posts)
            .values(
                likes_quantity=posts.c.likes_quantity + likes,
                dislikes_quantity=posts.c.dislikes_quantity + dislikes,
            )
            .where(
                posts.c.id == post_id,
            )
        )

        if new_rate is None:
            # Likes or dislike are reset
            await self._db_conn.execute(
                delete(post_rates).where(post_rates.c.post_id == post_id).where(post_rates.c.user_id == user_id)
            )
            return

        # Update user rate
        await self._db_conn.execute(
            insert(post_rates)
            .values(
                post_id=post_id,
                user_id=user_id,
                rate=new_rate,
            )
            .on_conflict_do_update(
                constraint=post_rates.primary_key,
                set_={post_rates.c.rate: new_rate},
            )
        )


class BadPostImageError(Exception):
    ...


class UnknownPostError(Exception):
    ...


class UnknownPostOrUserError(UnknownPostError, UnknownUserError):
    ...
