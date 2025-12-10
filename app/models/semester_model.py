from datetime import date, datetime, timezone

import ulid
from sqlmodel import Boolean, Column, Date, Field, Integer, SQLModel, String


class Semester(SQLModel, table=True):
    __tablename__ = "semester" 

    semester_id: str = Field(
        sa_column=Column(
            String(30),
            insert_default=lambda: ulid.new().str,
            primary_key=True,
            index=True,
        )
    )
    student_id: str = Field(foreign_key="student_info.student_id", nullable=False)
    semester_no: int = Field(sa_column=Column(Integer, default=None, nullable=False))

    pass_fail: bool = Field(sa_column=Column(Boolean, default=None, nullable=False))
    academic: str = Field(default=None, nullable=False)
    section: str = Field(default=None, nullable=False)
    start: date = Field(
        sa_column=Column(
            Date, nullable=False, default=lambda: datetime.now(timezone.utc)
        )
    )
    end: date = Field(sa_column=Column(Date, nullable=False))
