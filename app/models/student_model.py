from sqlmodel import SQLModel, Field, ForeignKey, String, Column, Relationship
from typing import Optional
import ulid

class StudentInfo(SQLModel, table=True):
    __tablename__ = "student_info"
    
    student_id: str = Field(
        default_factory=lambda: ulid.new().str,
        primary_key=True
    )
    
    user_id: str = Field(foreign_key="user.user_id", nullable=False, unique=True)
    student_number: int = Field(sa_column=Column(String(100), nullable=False))
    father_name: str = Field(sa_column=Column(String(100), nullable=False))
    mother_name: str = Field(sa_column=Column(String(100), nullable=False))
    nrc: str = Field(sa_column=Column(String(25), nullable=False))
    
    user: Optional["User"] = Relationship(back_populates="student_info")