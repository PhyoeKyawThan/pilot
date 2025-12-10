from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy.orm import sessionmaker
from typing import Annotated
from app.config import config

engine: AsyncEngine = create_async_engine(config.DATABASE_URL, echo=config.DATABASE_QUERY_ECHO)

async_session_maker = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)
