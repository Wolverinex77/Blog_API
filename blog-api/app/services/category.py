from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import exceptions
from app.models.category import Category
from app.models.post import Post
from app.schemas.category import CategoryCreate, CategoryUpdate


async def get_categories(db: AsyncSession) -> Sequence[Category]:
    result = await db.scalars(select(Category).order_by(Category.id))
    return result.all()


async def get_category(db: AsyncSession, category_id: int) -> Category:
    category = await db.get(Category, category_id)
    if category is None:
        raise exceptions.CategoryNotFound()
    return category


async def create_category(
    db: AsyncSession,
    category_data: CategoryCreate,
) -> Category:
    existing_category = await db.scalar(
        select(Category).where(Category.name == category_data.name)
    )
    if existing_category is not None:
        raise exceptions.CategoryAlreadyExists()

    category = Category(name=category_data.name)
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return category


async def update_category(
    db: AsyncSession,
    category_id: int,
    category_data: CategoryUpdate,
) -> Category:
    category = await get_category(db, category_id)

    existing_category = await db.scalar(
        select(Category).where(
            Category.name == category_data.name,
            Category.id != category_id,
        )
    )
    if existing_category is not None:
        raise exceptions.CategoryAlreadyExists()

    category.name = category_data.name
    await db.commit()
    await db.refresh(category)
    return category


async def delete_category(db: AsyncSession, category_id: int) -> None:
    category = await get_category(db, category_id)
    post_exists = await db.scalar(
        select(Post.id).where(Post.category_id == category_id).limit(1)
    )
    if post_exists is not None:
        raise exceptions.CategoryInUse()
    await db.delete(category)
    await db.commit()
