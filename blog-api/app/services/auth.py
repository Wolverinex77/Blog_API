from app.schemas.user import UserCreate, UserLogin
from app.models.user import User
from app.core.security import hash_password,verify_password,create_access_token
from app.core import exceptions
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


async def register_user(user:UserCreate,db:AsyncSession):
    
    existing_user = await db.scalar(
        select(User).where(User.email == user.email)
    )
    if existing_user:
        raise exceptions.EmailAlreadyExistsError()   

    existing_username = await db.scalar(
        select(User).where(User.username == user.username)
    )
    if existing_username:
        raise exceptions.UserNameAlreadyExistsError()
        
    db_user=User(
            username=user.username,
             email=user.email,
             hashed_password=hash_password(user.password),
             bio=user.bio,
             avatar_url=user.avatar_url,
             is_active=user.is_active
             )      
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user
async def  login_user(user:UserLogin,db:AsyncSession):
    stmt=select(User).where(User.email == user.email)
    result=await db.execute(stmt)
    db_user=result.scalars().one_or_none()
    if db_user is None or not db_user.is_active:
        raise exceptions.InvalidCredentialsError()
    if verify_password(user.password,db_user.hashed_password):
        return create_access_token(str(db_user.id))
    else:
        raise exceptions.InvalidCredentialsError()
