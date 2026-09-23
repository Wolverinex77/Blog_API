from sqlalchemy.orm import Mapped,mapped_column,relationship
from sqlalchemy import (
    INTEGER, Boolean,
    String,TIMESTAMP,text,func, true , Enum as SQLEnum)
from datetime import datetime
from app.core.database import Base
from enum import Enum

class UserRole(str,Enum):
    USER="user"
    ADMIN="admin"
    
    
class User(Base):
    __tablename__='users'
    id:Mapped[int]=mapped_column(INTEGER,primary_key=True,nullable=False)
    username:Mapped[str]=mapped_column(String,nullable=False,unique=True)
    email:Mapped[str]=mapped_column(String,nullable=False,unique=True)
    hashed_password:Mapped[str]=mapped_column(String,nullable=False)
    role:Mapped[UserRole]=mapped_column(SQLEnum(UserRole),nullable=False,default=UserRole.USER)
    bio:Mapped[str]=mapped_column(String,nullable=True)
    avatar_url:Mapped[str]=mapped_column(String,nullable=True)
    is_active:Mapped[bool]=mapped_column(Boolean,nullable=False,default=True)
        
    created_at: Mapped[TIMESTAMP] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text('NOW()')
    )
    updated_at: Mapped[datetime] = mapped_column(
    server_default=func.now(),
    onupdate=func.now()
        )
