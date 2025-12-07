from fastapi import APIRouter, Response, Depends, Request, status, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from app.models.student_model import StudentInfo
from typing import Annotated
from fastapi_jwt_auth2 import AuthJWT
from app.dependencies import get_session

student = APIRouter(prefix="/student")

class StudentSchema(BaseModel):
    student_number: int = Field(gt=0, title="The student registery number from begin of first year.")
    father_name: str = Field(title="Student's father name")
    mother_name: str = Field(title="Student's mother name")
    nrc: str | None = Field(
        default=None, 
        title="Student's NRC number", 
        examples="Example format: 14/LaMaNa(N)101010")
    

@student.post("/create")
async def create_student(student_info: StudentSchema, request: Request, dbSession: Annotated[AsyncSession, Depends(get_session)],Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    raw_jwt = Authorize.get_raw_jwt()
    if raw_jwt.get("role") == "student":
        try:
            student_model: StudentInfo = StudentInfo(
            user_id=raw_jwt.get("sub"),
            student_number=student_info.student_number,
            father_name=student_info.father_name,
            mother_name=student_info.mother_name,
            nrc=student_info.nrc
        )
            dbSession.add(student_model)
            await dbSession.commit()
            return JSONResponse(
                content="Student info created",
                status_code=status.HTTP_201_CREATED,
            )
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Student info already exists"
            )
        