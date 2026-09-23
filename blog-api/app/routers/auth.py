# app/routers/auth.py
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from fastapi import APIRouter,HTTPException
from app.services import auth
from app.schemas import user
from app.core import exceptions
from sqlalchemy.exc import IntegrityError
from app.core.database import get_async_db
router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

@router.post("/login")
async def login(user:user.UserLogin,db:AsyncSession=Depends(get_async_db)):
    try:
        return await auth.login_user(user=user,db=db)
    except exceptions.InvalidCredentialsError:
       raise HTTPException(status_code=401, detail="Invalid credentials")
@router.post("/register")
async def register(user:user.UserCreate,db:AsyncSession=Depends(get_async_db)):
    try:
        return await auth.register_user(user,db)
    
    except  exceptions.EmailAlreadyExistsError:
        raise HTTPException(status_code=409, detail="Email already exists")
    except exceptions.UserNameAlreadyExistsError:
        raise HTTPException(status_code=409, detail="Username already exists")
    
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Username already exists")
