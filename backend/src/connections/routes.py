from datetime import datetime, timedelta
import secrets
import uuid

from fastapi import APIRouter, HTTPException, Request, Response
import jwt
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from ..clients.redis_client import redis_client as redis
from ..connections.schemas import Credentials
from ..settings import EXPIRE_MINUTES, SECRET_KEY


router = APIRouter(prefix="/connections", tags=["connections"])


@router.post("/")
async def make_connection_token(credentials: Credentials, response: Response):
    token_id = str(uuid.uuid4()) 
    db_url = f"postgresql+asyncpg://{credentials.username}:{credentials.password}@{credentials.host}:{credentials.port}/{credentials.database}"
    engine = create_async_engine(db_url, future=True, echo=False, pool_size=5, max_overflow=10)
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    readonly_user = f"user_{uuid.uuid4().hex[:8]}"
    readonly_pass = secrets.token_urlsafe(12)

    async with async_session() as session:
        safe_user = readonly_user.replace('"', '""')
        safe_pass = readonly_pass.replace("'", "''")
        await session.execute(text(f'CREATE USER "{safe_user}" WITH PASSWORD \'{safe_pass}\''))
        await session.execute(text(f'GRANT CONNECT ON DATABASE "{credentials.database}" TO "{safe_user}"'))
        await session.execute(text(f'GRANT USAGE ON SCHEMA public TO "{safe_user}"'))
        await session.execute(text(f'GRANT SELECT ON ALL TABLES IN SCHEMA public TO "{safe_user}"'))
        await session.commit()
    await engine.dispose()
    db_url = f"postgresql+asyncpg://{readonly_user}:{readonly_pass}@{credentials.host}:{credentials.port}/{credentials.database}"

    payload = {
        "db_url": db_url,
        "exp": datetime.now() + timedelta(minutes=EXPIRE_MINUTES)
    }
    jwt_token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    await redis.set(f"dbtoken:{token_id}", jwt_token, ex=EXPIRE_MINUTES*60)
    response.set_cookie(
        key="db_token_id",
        value=token_id,
        httponly=True,
        max_age=EXPIRE_MINUTES*60,
        samesite="lax",
        secure=False  
    )
    return {"status": "token-issued"}

@router.get("/")
async def prolong_connection_token(request: Request, response: Response):
    token_id = request.cookies.get('db_token_id')
    if not token_id:
        raise HTTPException(status_code=401, detail="Token cookie not found")

    key = f"dbtoken:{token_id}"
    token_db = await redis.get(key)
    if not token_db:
        raise HTTPException(status_code=403, detail="Token not found in Redis")

    payload_data = jwt.decode(token_db, SECRET_KEY, algorithms=["HS256"])
    db_url = payload_data["db_url"]

 
    new_payload = {
        "db_url": db_url,
        "exp": datetime.now() + timedelta(minutes=EXPIRE_MINUTES)
    }
    new_jwt_token = jwt.encode(new_payload, SECRET_KEY, algorithm="HS256")

    await redis.set(key, new_jwt_token, ex=EXPIRE_MINUTES*60)

    response.set_cookie(
        key="db_token_id",
        value=token_id,
        httponly=True,
        max_age=EXPIRE_MINUTES*60,
        samesite="lax",
        secure=False
    )

    return {"status": "token-prolonged"}


#==================================================
# если хотите затестировать -> пользуйтесь 

# @router.get("/test")
# async def test(request: Request):
#     token_id = request.cookies.get('db_token_id')
#     if not token_id:
#         raise HTTPException(status_code=401, detail="Token cookie not found")
#     db_url = await get_dburl_user(token_id)
#     async for con in get_async_session_by_user(db_url):
#         result = await con.execute(text("SELECT * FROM habr"))
#         rows = result.fetchall() 
#         data = [dict(row._mapping) for row in rows]

#     return {"status": "ok", "data": data}