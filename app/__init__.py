from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.models.database import engine
from sqlmodel import SQLModel
from contextlib import asynccontextmanager
from app.routers.auth import auth
from app.routers.student import student
from fastapi_jwt_auth2 import AuthJWT
from fastapi_jwt_auth2.exceptions import AuthJWTException
from pydantic import BaseModel
from app.config import config
from starlette.middleware.sessions import SessionMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield
    await engine.dispose()

app = FastAPI(lifespan=lifespan)

class Settings(BaseModel):
    authjwt_secret_key: str = config.AUTHJWT_SECRET_KEY
    authjwt_token_location: list[str] = ["cookies"]
    authjwt_access_cookie_key: str = config.AUTHJWT_ACCESS_COOKIE_KEY
    authjwt_refresh_cookie_key: str = config.AUTHJWT_REFRESH_COOKIE_KEY
    authjwt_cookie_csrf_protect: bool = config.AUTHJWT_COOKIE_CSRF_PROTECT
    
@AuthJWT.load_config
def get_config():
    return Settings()

@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(
        status_code=401,
        content={
            "detail": str(exc)
        }
    )

# middlewares
app.add_middleware(
    SessionMiddleware,
    secret_key=config.SESSION_SECRET
)

app.include_router(auth)
app.include_router(student)
