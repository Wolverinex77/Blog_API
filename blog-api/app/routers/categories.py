from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import exceptions
from app.core.database import get_async_db
from app.dependencies.common import require_admin
from app.schemas.category import (
    CategoryCreate,
    CategoryResponse,
    CategoryUpdate,
)
from app.services.category import (
    create_category as create_category_service,
    delete_category as delete_category_service,
    get_categories as get_categories_service,
    get_category as get_category_service,
    update_category as update_category_service,
)

router = APIRouter(
    prefix="/categories",
    tags=["Categories"],
)


@router.get("/", response_model=list[CategoryResponse])
async def get_categories(
    db: AsyncSession = Depends(get_async_db),
):
    return await get_categories_service(db)


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: int,
    db: AsyncSession = Depends(get_async_db),
):
    try:
        return await get_category_service(db, category_id)
    except exceptions.CategoryNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )


@router.post(
    "/",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
async def create_category(
    category_data: CategoryCreate,
    db: AsyncSession = Depends(get_async_db),
):
    try:
        return await create_category_service(db, category_data)
    except exceptions.CategoryAlreadyExists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Category already exists",
        )


@router.patch(
    "/{category_id}",
    response_model=CategoryResponse,
    dependencies=[Depends(require_admin)],
)
async def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    db: AsyncSession = Depends(get_async_db),
):
    try:
        return await update_category_service(db, category_id, category_data)
    except exceptions.CategoryNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )
    except exceptions.CategoryAlreadyExists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Category already exists",
        )


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin)],
)
async def delete_category(
    category_id: int,
    db: AsyncSession = Depends(get_async_db),
):
    try:
        await delete_category_service(db, category_id)
    except exceptions.CategoryNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )
    except exceptions.CategoryInUse:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Category cannot be deleted while posts use it",
        )
