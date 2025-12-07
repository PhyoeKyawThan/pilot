from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel, Field
from sqlmodel import select
from app.dependencies import get_session, get_settings
from app.config import Config
from app.models.user import User
from typing import Annotated
from fastapi_jwt_auth2 import AuthJWT
from datetime import timedelta
auth = APIRouter(prefix="/auth/user")

class TokenSchema(BaseModel):
    access_token: str | None
    refresh_token: str | None

class UserCreateSchema(BaseModel):
    username: str
    first_name: str
    last_name: str
    email: str
    password: str

class UserLoginSchema(BaseModel):
    username: str | None 
    email: str | None
    password: str 

class ResponseSchema(BaseModel):
    status: bool
    message: str
    err_message: str | None = None
    

@auth.post("/signup", response_model=ResponseSchema)
async def singup(
    user: UserCreateSchema,
    dbSession: Annotated[AsyncSession, Depends(get_session)]
) -> ResponseSchema:
    if user:
        created_user: User = User(
             username=user.username,
             first_name=user.first_name,
             last_name=user.last_name,
             email=user.email,
            password=user.password
        )
        
        created_user.set_password(user.password)
        try:
            dbSession.add(created_user)
            await dbSession.commit()
            return ResponseSchema(
                status=True,
                message="User Created"
            )
        except IntegrityError as e:
            return ResponseSchema(
                status=False,
                message="Try using another mail or Login!",
                err_message=f"{user.email} already exists!"
            )
    return ResponseSchema(
        status=False,
        message=f"Require fields: {UserCreateSchema.model_dump()}"
    )

@auth.post("/login", response_model=ResponseSchema | TokenSchema)
async def login(
    user: UserLoginSchema,
    response: Response,
    dbSession: Annotated[AsyncSession, Depends(get_session)],
    config: Annotated[Config, Depends(get_settings)],
    Authorize: AuthJWT = Depends(),
) -> ResponseSchema | TokenSchema:
    if user.username or user.email and user.password:
        result = await dbSession.execute(select(User).where(User.email == user.email))
        found_user: User = result.scalars().first()
        if found_user:
            if(found_user.verify_password(user.password)):
                token_scheme: TokenSchema = TokenSchema(
                    access_token=Authorize.create_access_token(subject=user.username + user.email),
                    refresh_token=Authorize.create_refresh_token(subject=user.username + user.email)
                )
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
                    status=True,
                    message="User Verified!"
                )
            return ResponseSchema(
                status=False,
                message="Incorrect Username or Password!",
                err_message="Incorrect Username or Password"
            )
    raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail="Require username or email and password")

@auth.post("/refresh")
def refresh(Authorize: AuthJWT = Depends()):
    
    Authorize.jwt_refresh_token_required()
    
    current_user = Authorize.get_jwt_subject()
    new_access_token = Authorize.create_access_token(subject=current_user)
    return {
        "access_token": new_access_token
    }
    
@auth.get("/protected")
def protected(Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    
    current_user= Authorize.get_jwt_subject()
    return current_user

@auth.get("/settings")
def settings(settings: Annotated[Config, Depends(get_settings)]):
    return settings
    