from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import exceptions
from app.core.database import get_async_db
from app.dependencies.common import get_current_user, require_admin
from app.models.user import User
from app.schemas.post import PostResponse, SelectedTags
from app.schemas.tag import TagCreate, TagResponse
from app.services.tag import (
    add_selected_tags as add_selected_tags_service,
    create_tag as create_tag_service,
    get_tags as get_tags_service,
    suggest_post_tags as suggest_post_tags_service,
)

router = APIRouter(
    prefix="/tags",
    tags=["Tags"],
)


@router.get("/", response_model=list[TagResponse])
async def get_tags(db: AsyncSession = Depends(get_async_db)):
    return await get_tags_service(db)


@router.post("/posts/{post_id}/suggest-tags")
async def suggest_post_tags(
    post_id: int,
    db: AsyncSession = Depends(get_async_db),
):
    try:
        tags = await suggest_post_tags_service(db, post_id)
        return {"suggested_tags": tags}
    except exceptions.PostNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )
    except exceptions.GeminiResponseError:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Could not generate tag suggestions",
        )


@router.post(
    "/posts/{post_id}/selected-tags",
    response_model=PostResponse,
)
async def add_selected_tags(
    post_id: int,
    selected_tags: SelectedTags,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return await add_selected_tags_service(
            db,
            current_user,
            post_id,
            selected_tags.suggested_tags,
        )
    except exceptions.PostNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )


@router.post(
    "/",
    response_model=TagResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
async def create_tag(
    tag_data: TagCreate,
    db: AsyncSession = Depends(get_async_db),
):
    try:
        return await create_tag_service(db, tag_data)
    except exceptions.TagAlreadyExists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Tag already exists",
        )
