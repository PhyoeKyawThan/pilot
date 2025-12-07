from fastapi import APIRouter, Depends, HTTPException, status, Response, Request, logger
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel, Field
from sqlmodel import select
from app.dependencies import get_session, get_settings
from app.config import Config
from app.models.user import User, UserRole
from typing import Annotated
from fastapi_jwt_auth2 import AuthJWT
from fastapi_jwt_auth2.exceptions import AuthJWTException
from datetime import timedelta

auth = APIRouter(prefix="/auth/user")

class TokenSchema(BaseModel):
    access_token: str | None
    refresh_token: str | None

class UserCreateSchema(BaseModel):
    username: str
    user_role: UserRole
    first_name: str
    last_name: str
    email: str
    password: str

class UserLoginSchema(BaseModel):
    username: str | None 
    # user_role: UserRole
    email: str | None
    password: str 

class ResponseSchema(BaseModel):
    status_code: int
    message: str
    err_message: str | None = None
 
@auth.post("/signup", response_model=ResponseSchema)
async def singup(
    user: UserCreateSchema,
    dbSession: Annotated[AsyncSession, Depends(get_session)]
) -> ResponseSchema:
    created_user: User = User(
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        user_role=user.user_role,
        email=user.email,
        password=user.password
    )
    
    created_user.set_password(user.password)
    try:
        dbSession.add(created_user)
        await dbSession.commit()
        return ResponseSchema(
            status_code=status.HTTP_201_CREATED,
            message="User Created"
        )
    except IntegrityError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Account already exists",
        )

@auth.post("/login", response_model=ResponseSchema | TokenSchema)
async def login(
    user: UserLoginSchema,
    response: Response,
    request: Request,
    dbSession: Annotated[AsyncSession, Depends(get_session)],
    config: Annotated[Config, Depends(get_settings)],
    Authorize: AuthJWT = Depends(),
) -> ResponseSchema | TokenSchema:
    
    access_token: str | None = request.cookies.get("access_token_cookie")
    refresh_token: str | None= request.cookies.get("refresh_token_cookie")
    if access_token and refresh_token:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User Already Logged in"
            )
    result = await dbSession.execute(select(User).where(User.email == user.email))
    found_user: User = result.scalars().first()
    if found_user:
        if(found_user.verify_password(user.password)):
            token_scheme: TokenSchema = TokenSchema(
                access_token=Authorize.create_access_token(subject=found_user.user_id),
                refresh_token=Authorize.create_refresh_token(subject=user.username+user.email)
            )
            request.session['user_id'] = found_user.user_id
            request.session['user_role'] = found_user.user_role
            Authorize.set_access_cookies(
                token_scheme.access_token, 
                response=response,
                max_age=int(timedelta(hours=config.AUTHJWT_ACCESS_EXPIRE_HOUR).total_seconds()),
            )
            Authorize.set_refresh_cookies(
                token_scheme.refresh_token, 
                response=response,
                max_age=int(timedelta(days=config.AUTHJWT_REFRESH_EXPIRE_DAY).total_seconds()))
            return ResponseSchema(
                status_code=status.HTTP_200_OK,
                message="User Verified!"
            )
        return ResponseSchema(
            status_code=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION,
            message="Incorrect Username or Password!",
            err_message="Incorrect Username or Password"
        )

    
@auth.post("/refresh")
def refresh(config: Annotated[Config, Depends(get_settings)], request: Request, response: Response, Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_refresh_token_required()
    
        current_user = Authorize.get_jwt_subject()
        new_access_token = Authorize.create_access_token(subject=current_user)
        Authorize.set_access_cookies(
            new_access_token,
            response=response,
            max_age=int(timedelta(hours=config.AUTHJWT_ACCESS_EXPIRE_HOUR).total_seconds())
        )
        return {
            "message": "Token refreshed!"
        }
    except AuthJWTException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expired",
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server Error"
        ) 
@auth.get("/protected")
def protected(Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    
    current_user= Authorize.get_jwt_subject()
    return current_user

# @auth.get("/settings")
# def settings(settings: Annotated[Config, Depends(get_settings)]):
    # return settings
    # 