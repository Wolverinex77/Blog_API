from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import exceptions
from app.models.comment import Comment
from app.models.post import Post
from app.models.user import User
from app.schemas.comment import CommentCreate, CommentUpdate


async def get_comments(
    db: AsyncSession,
    post_id: int | None = None,
) -> Sequence[Comment]:
    query = select(Comment).order_by(Comment.created_at)
    if post_id is not None:
        query = query.where(Comment.post_id == post_id)
    result = await db.scalars(query)
    return result.all()


async def get_comment(db: AsyncSession, comment_id: int) -> Comment:
    comment = await db.get(Comment, comment_id)
    if comment is None:
        raise exceptions.CommentNotFound()
    return comment


async def create_comment(
    db: AsyncSession,
    current_user: User,
    comment_data: CommentCreate,
) -> Comment:
    post = await db.get(Post, comment_data.post_id)
    if post is None:
        raise exceptions.PostNotFound()

    comment = Comment(
        content=comment_data.content,
        post_id=comment_data.post_id,
        user_id=current_user.id,
    )
    db.add(comment)
    await db.commit()
    await db.refresh(comment)
    return comment


async def update_comment(
    db: AsyncSession,
    current_user: User,
    comment_id: int,
    comment_data: CommentUpdate,
) -> Comment:
    comment = await get_comment(db, comment_id)
    if comment.user_id != current_user.id:
        raise exceptions.CommentNotFound()

    comment.content = comment_data.content
    await db.commit()
    await db.refresh(comment)
    return comment


async def delete_comment(
    db: AsyncSession,
    current_user: User,
    comment_id: int,
) -> None:
    comment = await get_comment(db, comment_id)
    if comment.user_id != current_user.id:
        raise exceptions.CommentNotFound()

    await db.delete(comment)
    await db.commit()


async def delete_comment_as_admin(
    db: AsyncSession,
    comment_id: int,
) -> None:
    comment = await get_comment(db, comment_id)
    await db.delete(comment)
    await db.commit()
