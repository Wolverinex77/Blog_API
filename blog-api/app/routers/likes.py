# app/routers/likes.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.post import PostResponse
from app.core import exceptions
from app.core.database import get_async_db
from app.dependencies.common import get_current_user
from app.models.user import User
from app.services.like import (
    create_like as create_like_service,
    delete_like as delete_like_service,
)

router = APIRouter(
    prefix="/likes",
    tags=["Likes"]
)

@router.get("/")
async def get_likes(
    db: AsyncSession = Depends(get_async_db),
):
    return {"message": "likes"}


@router.post("/{post_id}",response_model=PostResponse)
async def create_like(
    post_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return await create_like_service(db, current_user, post_id)
    except exceptions.PostNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_like(
    post_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    try:
        await delete_like_service(db, current_user, post_id)
    except exceptions.LikeNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Like not found",
        )
