import os

from typing import AsyncGenerator
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from fastapi_users.db import SQLAlchemyUserDatabase

from ..models import Base
from ..models.database import User


load_dotenv()
DATABASE_NAME = os.getenv("DATABASE_NAME", "outageoracle.db") # noqa
engine = create_async_engine(f'sqlite+aiosqlite:///./{DATABASE_NAME}') # noqa
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False) # noqa


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)
