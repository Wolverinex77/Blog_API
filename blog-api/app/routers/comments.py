from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import exceptions
from app.core.database import get_async_db
from app.dependencies.common import get_current_user, require_admin
from app.models.user import User
from app.schemas.comment import CommentCreate, CommentResponse, CommentUpdate
from app.services.comment import (
    create_comment as create_comment_service,
    delete_comment as delete_comment_service,
    delete_comment_as_admin as delete_comment_as_admin_service,
    get_comment as get_comment_service,
    get_comments as get_comments_service,
    update_comment as update_comment_service,
)

router = APIRouter(
    prefix="/comments",
    tags=["Comments"],
)
admin_router = APIRouter(
    prefix="/admin/comments",
    tags=["Admin Comments"],
)


@router.get("/", response_model=list[CommentResponse])
async def get_comments(
    post_id: int | None = Query(None),
    db: AsyncSession = Depends(get_async_db),
):
    return await get_comments_service(db, post_id)


@router.get("/{comment_id}", response_model=CommentResponse)
async def get_comment(
    comment_id: int,
    db: AsyncSession = Depends(get_async_db),
):
    try:
        return await get_comment_service(db, comment_id)
    except exceptions.CommentNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )


@router.post(
    "/",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_comment(
    comment_data: CommentCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return await create_comment_service(db, current_user, comment_data)
    except exceptions.PostNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )


@router.patch("/{comment_id}", response_model=CommentResponse)
async def update_comment(
    comment_id: int,
    comment_data: CommentUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return await update_comment_service(
            db,
            current_user,
            comment_id,
            comment_data,
        )
    except exceptions.CommentNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    try:
        await delete_comment_service(db, current_user, comment_id)
    except exceptions.CommentNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )


@admin_router.delete(
    "/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin)],
)
async def delete_comment_as_admin(
    comment_id: int,
    db: AsyncSession = Depends(get_async_db),
):
    try:
        await delete_comment_as_admin_service(db, comment_id)
    except exceptions.CommentNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )
