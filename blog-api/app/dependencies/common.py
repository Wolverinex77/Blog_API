from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import exceptions
from app.core.database import get_async_db
from app.core.security import decode_access_token, oauth2_scheme
from app.models.user import User, UserRole


async def get_current_user(
	token: str = Depends(oauth2_scheme),
	db: AsyncSession = Depends(get_async_db),
) -> User:
	user_id = decode_access_token(token)
	if user_id is None:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Could not validate credentials",
		)

	try:
		current_user = await db.get(User, int(user_id))
	except (TypeError, ValueError):
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Could not validate credentials",
		)

	if current_user is None or not current_user.is_active:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Could not validate credentials",
		)

	return current_user


async def require_admin(
	current_user: User = Depends(get_current_user),
) -> User:
	if current_user.role != UserRole.ADMIN:
		raise HTTPException(
			status_code=status.HTTP_403_FORBIDDEN,
			detail="Admin access required",
		)

	return current_user
