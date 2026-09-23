from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core import exceptions
from app.core.security import hash_password
from app.models.user import User
from app.schemas.user import UpdateProfile


async def get_current_user_profile(db: AsyncSession, user_id: int) -> User | None:
	return await db.get(User, user_id)


async def get_all_users(db: AsyncSession) -> Sequence[User]:
    result = await db.scalars(select(User))
    return result.all()

async def update_user(
	db: AsyncSession, user_id: int, user_data: UpdateProfile
) -> User:
	user = await db.get(User, user_id)
	if user is None:
		raise exceptions.UserNotFound()

	data = user_data.model_dump(exclude_unset=True)
	if "email" in data and data["email"] != user.email:
		existing_user = await db.scalar(
			select(User).where(User.email == data["email"])
		)
		if existing_user:
			raise exceptions.EmailAlreadyInUseError()

	if "name" in data:
		existing_user = await db.scalar(
			select(User).where(
				User.username == data["name"],
				User.id != user_id,
			)
		)
		if existing_user:
			raise exceptions.UserNameAlreadyExistsError()
		user.username = data.pop("name")
	if "password" in data:
		user.hashed_password = hash_password(data.pop("password"))

	for field, value in data.items():
		setattr(user, field, value)

	await db.commit()
	await db.refresh(user)
	return user


async def delete_user(db: AsyncSession, user_id: int) -> None:
	user = await db.get(User, user_id)
	if user is None:
		raise exceptions.UserNotFound()

	await db.delete(user)
	await db.commit()
