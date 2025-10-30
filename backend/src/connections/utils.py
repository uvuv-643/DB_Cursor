import os

from fastapi import HTTPException
import jwt
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from ..clients.redis_client import redis_client as redis
from settings import SECRET_KEY


async def get_dburl_user(key: str)->str:
    """
    Извлекает строку подключения к базе данных (DB URL) из Redis по ключу токена. 

    Args:
        key (str): Ключ токена, по которому осуществляется поиск в Redis. Обычно лежит в Cookie под db_user
    Returns:
        str: Строка подключения к базе данных в формате SQLAlchemy,
            например `"postgresql+asyncpg://user:password@host:port/database"`.

    Raises:
        HTTPException: Если токен не найден в Redis (код 403).
        jwt.exceptions.DecodeError: Если токен некорректен или повреждён.
        jwt.exceptions.ExpiredSignatureError: Если срок действия токена истёк.

    Example:
        >>> db_url = await get_dburl_user("user_12345")
        >>> print(db_url)
        postgresql+asyncpg://postgres:password@localhost:5432/mydb
    """
    key = f"dbtoken:{key}"
    token_db = await redis.get(key)

    if not token_db:
        raise HTTPException(status_code=403, detail="Token not found in Redis")

    payload_data = jwt.decode(token_db, SECRET_KEY, algorithms=["HS256"])
    db_url = payload_data["db_url"]
    return db_url




async def get_async_session_by_user(db_url:str):
    """
    [Асинхронный генератор]Создаёт асинхронную сессию SQLAlchemy (AsyncSession) на основе переданной строки подключения.

    Пример:
        >>> async for session in get_async_session_by_user("postgresql+asyncpg://postgres:qwery42@localhost:5432/postgres"):
        ...     result = await session.execute("SELECT 1")

    Args:
        db_url (str): Строка подключения к базе данных в формате SQLAlchemy, 
            например `"postgresql+asyncpg://user:password@host:port/database"`.

    Yields:
        AsyncSession: Асинхронная сессия SQLAlchemy для выполнения запросов к базе данных.
 
    """
    engine = create_async_engine(db_url, future=True, echo=False, pool_size=5, max_overflow=10)
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async with async_session() as session:
        yield session

    await engine.dispose()  


 