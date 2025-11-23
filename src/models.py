# src/models.py
from pydantic import BaseModel
from typing import Optional, List

class Employee(BaseModel):
    id: str
    name: str
    email: str
    department: str
    position: str
    hire_date: str
    salary: Optional[float] = None
    manager: Optional[str] = None

class LeaveRequest(BaseModel):
    id: str
    employee_id: str
    start_date: str
    end_date: str
    leave_type: str
    reason: str
    status: str
    submitted_date: str

class LeaveRequestCreate(BaseModel):
    employee_id: str
    start_date: str
    end_date: str
    leave_type: str
    reason: str