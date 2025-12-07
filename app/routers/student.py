from fastapi import APIRouter, Response, Depends
from pydantic import BaseModel, Field
from fastapi_jwt_auth2 import AuthJWT

student = APIRouter(prefix="/student")

class StudentSchema(BaseModel):
    student_number: int = Field(gt=0, title="The student registery number from begin of first year.", min_length=4)
    father_name: str = Field(title="Student's father name", min_length=6)
    mother_name: str = Field(title="Student's mother name", min_length=6)
    nrc: str | None = Field(default=None, title="Student's NRC number", examples="Example format: 14/LaMaNa(N)101010")
    

@student.post("/create")
def create_student(student_info: StudentSchema, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    
    