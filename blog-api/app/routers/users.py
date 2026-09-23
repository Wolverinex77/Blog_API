# app/routers/users.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import exceptions
from app.core.database import get_async_db
from app.dependencies.common import get_current_user, require_admin
from app.schemas.user import UpdateProfile, UserResponse
from app.services.user import delete_user, get_all_users, get_current_user_profile, update_user

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.get("/admin", response_model=list[UserResponse])
async def get_all_users_for_admin(
    db: AsyncSession = Depends(get_async_db),
    current_user=Depends(require_admin),
):
    return await get_all_users(db)


@router.get("/me", response_model=UserResponse)
async def get_user(
    db: AsyncSession = Depends(get_async_db),
    current_user=Depends(get_current_user),
):
    return await get_current_user_profile(db, current_user.id)


@router.patch("/me", response_model=UserResponse)
async def update_current_user(
    user_data: UpdateProfile,
    db: AsyncSession = Depends(get_async_db),
    current_user=Depends(get_current_user),
):
    try:
        return await update_user(db, current_user.id, user_data)
    except exceptions.UserNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    except exceptions.EmailAlreadyInUseError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists")
    except exceptions.UserNameAlreadyExistsError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already exists")


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_current_user(
    db: AsyncSession = Depends(get_async_db),
    current_user=Depends(get_current_user),
):
    try:
        await delete_user(db, current_user.id)
    except exceptions.UserNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
