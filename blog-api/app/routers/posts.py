# app/routers/posts.py

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_db
from app.core import exceptions
from app.dependencies.common import get_current_user
from app.models.user import User
from app.schemas.post import (
    PostCreate,
    PostCreateStatus,
    PostDetailResponse,
    PostListResponse,
    PostResponse,
    PostUpdate,
    PostUpdateStatus,
)
from app.services.post import (
    create_post as create_post_service,
    get_published_post,
    get_published_posts,
    delete_post as delete_post_service,
    update_post as update_post_service,
)
from slugify import slugify

router = APIRouter(
    prefix="/posts",
    tags=["Posts"]
)

@router.get("", response_model=list[PostListResponse])
async def get_posts(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    search: str | None = Query(None),
    category: str | None = Query(None),
    tag: str | None = Query(None),
    author_id: int | None = Query(None),
    sort: str | None = Query(None, pattern="^(newest|oldest)$"),
    db: AsyncSession = Depends(get_async_db),
):
    return await get_published_posts(
        db,
        page=page,
        limit=limit,
        search=search,
        category=category,
        tag=tag,
        author_id=author_id,
        sort=sort,
    )


@router.get("/{post_id}", response_model=PostDetailResponse)
async def get_post(
    post_id: int,
    db: AsyncSession = Depends(get_async_db),
):
    try:
        return await get_published_post(db, post_id)
    except exceptions.PostNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

@router.post("/")
async def create_post(
    title: str = Form(...),
    content: str = Form(...),
    excerpt: str = Form(...),
    post_status: PostCreateStatus = Form(..., alias="status"),
    category_id: int = Form(...),
    tags: list[str] = Form(default_factory=list),
    image: UploadFile | None = File(None),
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    post_data = PostCreate(
        title=title,
        slug=slugify(title),
        content=content,
        excerpt=excerpt,
        status=post_status,
        category_id=category_id,
        tags=tags,
    )
    try:
        return await create_post_service(db, current_user, post_data, image)
    except exceptions.InvalidImageTypeError:
        raise HTTPException(
            status_code=400,
            detail="Only JPEG, PNG and WebP images are allowed",
        )
    except exceptions.ImageTooLargeError:
        raise HTTPException(
            status_code=400,
            detail="Image must be smaller than 5 MB",
        )
    except exceptions.InvalidImageError:
        raise HTTPException(status_code=400, detail="Invalid image file")
    except exceptions.ImageFormatError:
        raise HTTPException(
            status_code=400,
            detail="Could not determine image format",
        )
    except exceptions.CategoryNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )
    except exceptions.PostSlugAlreadyExists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A post with this title already exists",
        )


# PATCH   /posts/{post_id}
@router.patch("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: int,
    title: str | None = Form(None),
    content: str | None = Form(None),
    excerpt: str | None = Form(None),
    post_status: PostUpdateStatus | None = Form(None, alias="status"),
    tags: list[str] | None = Form(None),
    image: UploadFile | None = File(None),
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    post_data = PostUpdate(
        title=title,
        content=content,
        excerpt=excerpt,
        status=post_status,
        tags=tags,
    )
    try:
        return await update_post_service(
            db, current_user, post_id, post_data, image
        )
    except exceptions.PostNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )
    except exceptions.InvalidImageTypeError:
        raise HTTPException(
            status_code=400,
            detail="Only JPEG, PNG and WebP images are allowed",
        )
    except exceptions.ImageTooLargeError:
        raise HTTPException(
            status_code=400,
            detail="Image must be smaller than 5 MB",
        )
    except exceptions.InvalidImageError:
        raise HTTPException(status_code=400, detail="Invalid image file")
    except exceptions.ImageFormatError:
        raise HTTPException(
            status_code=400,
            detail="Could not determine image format",
        )


# DELETE  /posts/{post_id}
@router.delete("/{post_id}")
async def delete_post(
    post_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    try:
        await delete_post_service(db, current_user, post_id)
        return {"message": "Post deleted successfully"}
    except exceptions.PostNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )
