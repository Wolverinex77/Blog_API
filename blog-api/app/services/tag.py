from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from app.core import exceptions
from app.models.post import Post
from app.services.gemini import suggest_tags
from app.models.tag import Tag
from app.models.user import User
from app.schemas.tag import TagCreate


async def get_tags(db: AsyncSession) -> list[Tag]:
    result = await db.scalars(select(Tag).order_by(Tag.name))
    return list(result.all())


async def create_tag(db: AsyncSession, tag_data: TagCreate) -> Tag:
    name = tag_data.name.strip().lower()
    existing_tag = await db.scalar(select(Tag).where(Tag.name == name))
    if existing_tag is not None:
        raise exceptions.TagAlreadyExists()

    tag = Tag(name=name)
    db.add(tag)
    await db.commit()
    await db.refresh(tag)
    return tag

async def suggest_post_tags(
    db: AsyncSession,
    post_id: int,
) -> list[str]:
    post = await db.get(Post, post_id)
    if post is None:
        raise exceptions.PostNotFound()

    return await suggest_tags(
        title=post.title,
        content=post.content,
    )

async def add_selected_tags(
    db: AsyncSession,
    current_user: User,
    post_id: int,
    selected_tags: list[str],
):
    post = await db.scalar(
        select(Post)
        .options(selectinload(Post.tags))
        .where(Post.id == post_id)
    )

    if post is None or post.author_id != current_user.id:
        raise exceptions.PostNotFound()

    tag_names = {tag.strip().lower() for tag in selected_tags if tag.strip()}

    tags = list(
        await db.scalars(
            select(Tag).where(Tag.name.in_(tag_names))
        )
    )

    existing_names = {tag.name for tag in tags}

    for tag_name in tag_names - existing_names:
        tag = Tag(name=tag_name)
        db.add(tag)
        tags.append(tag)

    post.tags = tags

    await db.commit()
    await db.refresh(post, ["tags"])
    return post