from sqlmodel import SQLModel, Field, ForeignKey
from user import User
import ulid

class StudentInfo(SQLModel, table=True):
    __tablename__ = "student_info"
    
    student_id: str = Field(
        default_factory=lambda: ulid.new().str,
        primary_key=True
    )
    
    user_id: str = Field(default=None, foreign_key="user.user_id", nullable=False)
    student_number: int = Field(nullable=False, min_length=3)
    father_name: str = Field(nullable=False, min_length=6)
    mother_name: str = Field(nullable=False, min_length=6)
    nrc: str = Field(nullable=False, min_length=10)