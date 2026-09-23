import logging

from fastapi import UploadFile
from datetime import datetime, timezone

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core import exceptions
from app.models.like import PostLike
from app.models.post import Post
from app.models.category import Category
from app.models.tag import Tag
from app.models.user import User
from app.schemas.post import (
    PostAuthorResponse,
    PostCategoryResponse,
    PostCreate,
    PostDetailResponse,
    PostListResponse,
    PostTagResponse,
    PostUpdate,
)
from app.schemas.comment import CommentResponse
from app.services.image import save_image
from slugify import slugify

logger = logging.getLogger(__name__)


async def create_post(
    db: AsyncSession,
    current_user: User,
    post_data: PostCreate,
    image: UploadFile | None = None,
):
    cover_image_url = post_data.cover_image_url
    category = await db.get(Category, post_data.category_id)
    if category is None:
        raise exceptions.CategoryNotFound()

    slug = slugify(post_data.title)
    existing_slug = await db.scalar(select(Post).where(Post.slug == slug))
    if existing_slug is not None:
        raise exceptions.PostSlugAlreadyExists()

    if image is not None:
        cover_image_url = await save_image(image)

    post = Post(
        title=post_data.title,
        slug=slug,
        content=post_data.content,
        excerpt=post_data.excerpt,
        status=post_data.status,
        author_id=current_user.id,
        category_id=post_data.category_id,
        cover_image_url=cover_image_url,
        published_at=(
            datetime.now(timezone.utc)
            if post_data.status.value == "published"
            else None
        ),
    )
    tag_names = {
        tag.strip().lower()
        for tag in post_data.tags
        if tag.strip()
    }
    if tag_names:
        post.tags = list(
            await db.scalars(
                select(Tag).where(Tag.name.in_(tag_names))
            )
        )
        existing_names = {tag.name for tag in post.tags}
        for tag_name in tag_names - existing_names:
            post.tags.append(Tag(name=tag_name))
    db.add(post)
    await db.commit()
    await db.refresh(post)
    return post


async def get_published_posts(
    db: AsyncSession,
    page: int = 1,
    limit: int = 10,
    search: str | None = None,
    category: str | None = None,
    tag: str | None = None,
    author_id: int | None = None,
    sort: str | None = None,
) -> list[PostListResponse]:
    query = (
        select(Post, func.count(PostLike.id))
        .options(selectinload(Post.author))
        .outerjoin(PostLike, PostLike.post_id == Post.id)
        .where(Post.status == "published")
    )

    if search:
        search_pattern = f"%{search}%"
        query = query.where(
            or_(
                Post.title.ilike(search_pattern),
                Post.content.ilike(search_pattern),
                Post.excerpt.ilike(search_pattern),
            )
        )

    if category:
        query = query.where(Post.category.has(name=category))

    if tag:
        query = query.where(Post.tags.any(Tag.name == tag))

    if author_id is not None:
        query = query.where(Post.author_id == author_id)

    if sort == "oldest":
        query = query.order_by(Post.created_at.asc())
    else:
        query = query.order_by(Post.created_at.desc())

    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit).group_by(Post.id)

    result = await db.execute(
        query
    )

    responses = []
    for post, likes in result.all():
        if post.author is None:
            raise exceptions.UserNotFound()
        responses.append(
            PostListResponse(
                id=post.id,
                title=post.title,
                slug=post.slug,
                excerpt=post.excerpt,
                cover_image_url=post.cover_image_url,
                author=PostAuthorResponse(
                    id=post.author.id,
                    username=post.author.username,
                ),
                likes=likes,
                created_at=post.created_at,
            )
        )

    return responses


async def get_published_post(
    db: AsyncSession,
    post_id: int,
) -> PostDetailResponse:
    post = await db.scalar(
        select(Post)
        .options(
            selectinload(Post.category),
            selectinload(Post.tags),
            selectinload(Post.comments),
        )
        .where(Post.id == post_id, Post.status == "published")
    )
    if post is None:
        raise exceptions.PostNotFound()

    author = await db.get(User, post.author_id)
    if author is None:
        raise exceptions.UserNotFound()

    likes = await db.scalar(
        select(func.count())
        .select_from(PostLike)
        .where(PostLike.post_id == post.id)
    )

    return PostDetailResponse(
        id=post.id,
        title=post.title,
        slug=post.slug,
        content=post.content,
        excerpt=post.excerpt,
        cover_image_url=post.cover_image_url,
        author=PostAuthorResponse(id=author.id, username=author.username),
        likes=likes or 0,
        status=post.status.value,
        author_id=post.author_id,
        category_id=post.category_id,
        category=PostCategoryResponse.model_validate(post.category),
        tags=[PostTagResponse.model_validate(tag) for tag in post.tags],
        comments=[
            CommentResponse.model_validate(comment)
            for comment in post.comments
        ],
        published_at=post.published_at,
        created_at=post.created_at,
        updated_at=post.updated_at,
    )


async def update_post(
    db: AsyncSession,
    current_user: User,
    post_id: int,
    post_data: PostUpdate,
    image: UploadFile | None = None,
):
    post = await db.get(Post, post_id)
    logger.info("Post Data: %s", post)

    if post is None:
        raise exceptions.PostNotFound()

    if post.author_id != current_user.id:
        raise exceptions.PostNotFound()

    data = post_data.model_dump(exclude_unset=True, exclude_none=True)

    tags = data.pop("tags", None)

    for field, value in data.items():
        setattr(post, field, value)

    if "status" in data:
        if data["status"].value == "published":
            post.published_at = post.published_at or datetime.now(timezone.utc)
        else:
            post.published_at = None

    if tags is not None:
        await db.refresh(post, ["tags"])
        tag_names = {
            tag.strip().lower()
            for tag in tags
            if tag.strip()
        }
        post.tags = list(
            await db.scalars(
                select(Tag).where(Tag.name.in_(tag_names))
            )
        )
        existing_names = {tag.name for tag in post.tags}
        for tag_name in tag_names - existing_names:
            post.tags.append(Tag(name=tag_name))
    
    if image is not None:
        logger.info("Image received: %s", image.filename)
        url = await save_image(image)
        logger.info("Image saved: %s", url)
        post.cover_image_url = url

    await db.commit()
    await db.refresh(post)
    return post


async def delete_post(
    db: AsyncSession,
    current_user: User,
    post_id: int,
) -> None:
    post = await db.get(Post, post_id)

    if post is None or post.author_id != current_user.id:
        raise exceptions.PostNotFound()

    await db.delete(post)
    await db.commit()