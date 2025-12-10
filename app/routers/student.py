from fastapi import APIRouter, Response, Depends, Request, status, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from app.models.student_model import StudentInfo
from app.models.semester_model import Semester
from app.models.user_model import User
from typing import Annotated
from fastapi_jwt_auth2 import AuthJWT
from app.dependencies import get_session
from datetime import date

student = APIRouter(prefix="/student")

class StudentSchema(BaseModel):
    student_number: int = Field(gt=0, title="The student registery number from begin of first year.")
    father_name: str = Field(title="Student's father name")
    mother_name: str = Field(title="Student's mother name")
    nrc: str | None = Field( default=None, title="Student's NRC number")
    

@student.post("/create")
async def create_student(
    student_info: StudentSchema, 
    request: Request, 
    dbSession: Annotated[AsyncSession, Depends(get_session)],
    Authorize: AuthJWT = Depends()):
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

class SemesterSchema(BaseModel):
    student_id: str | None = None
    semester_no: int

    pass_fail: bool
    academic: str 
    section: str 
    start: date
    end: date

async def get_existing_semester(student_id: str, semester_no: int, dbSession: AsyncSession) -> Semester:
    stmt = select(Semester).where(Semester.student_id == student_id and Semester.semester_no == semester_no)
    result = await dbSession.execute(stmt)
    semester: Semester | None = result.scalar_one_or_none()
    return semester

import json
@student.post("/semester/create")
async def create_semester(
    semester_detail: SemesterSchema,
    request: Request,
    dbSession: Annotated[AsyncSession, Depends(get_session)],
    Authorize: AuthJWT = Depends()
):
    
    Authorize.jwt_required()
    subject = Authorize.get_jwt_subject() # will return user id

    try:
        result = await dbSession.execute(select(StudentInfo).
                                        options(selectinload(StudentInfo.user)).where(StudentInfo.user_id == subject))
        student: StudentInfo | None = result.scalar_one_or_none()
        if student:
            semester = False
            semester: Semester = await get_existing_semester(student_id=student.student_id, semester_no=semester_detail.semester_no, dbSession=dbSession)
            if semester:
                return {
                        # "status_code":status.HTTP_409_CONFLICT,
                        "message": "Semester detail exists, No actions.",
                        "info": {
                            "semester_detail": semester,
                            "user": {
                            "username": student.user.username,
                            "father_name": student.father_name
                        }
                    }
                }
                
            semester_detail.student_id = student.student_id
            dbSession.add(Semester(**semester_detail.model_dump()))
            await dbSession.commit()
            return {
                "message": f"Successfully created semester for {student.user.username}",
                "info": {
                    "semester_detail": semester_detail,
                    "user": {
                        "username": student.user.username,
                        "father_name": student.father_name
                    }
                }
            }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Something wrong while inserting to database"
        )