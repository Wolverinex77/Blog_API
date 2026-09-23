from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import exceptions
from app.models.like import PostLike
from app.models.post import Post
from app.models.user import User

async def create_like(
    db: AsyncSession,
    current_user: User,
    post_id: int,
):
    post = await db.get(Post, post_id)
    if post is None:
        raise exceptions.PostNotFound()

    post_like = PostLike(
        user_id=current_user.id,
        post_id=post_id,
    )
    db.add(post_like)
    await db.commit()
    return post


async def delete_like(
    db: AsyncSession,
    current_user: User,
    post_id: int,
) -> None:
    post_like = await db.scalar(
        select(PostLike).where(
            PostLike.post_id == post_id,
            PostLike.user_id == current_user.id,
        )
    )
    if post_like is None:
        raise exceptions.LikeNotFound()

    await db.delete(post_like)
    await db.commit()