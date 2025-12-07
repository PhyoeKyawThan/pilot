from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.database import async_session_maker
from app.config import Config

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

def get_settings() -> Config:
    return Config()