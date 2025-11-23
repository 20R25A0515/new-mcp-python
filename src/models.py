# src/models.py
from pydantic import BaseModel, ConfigDict
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

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "EMP001",
                "name": "John Doe",
                "email": "john.doe@company.com",
                "department": "Engineering",
                "position": "Software Engineer",
                "hire_date": "2022-01-15",
                "salary": 75000.00,
                "manager": "Jane Smith"
            }
        }
    )

class LeaveRequest(BaseModel):
    id: str
    employee_id: str
    start_date: str
    end_date: str
    leave_type: str
    reason: str
    status: str
    submitted_date: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "LEAVE001",
                "employee_id": "EMP001",
                "start_date": "2024-01-10",
                "end_date": "2024-01-12",
                "leave_type": "Vacation",
                "reason": "Family vacation",
                "status": "approved",
                "submitted_date": "2023-12-15"
            }
        }
    )

class LeaveRequestCreate(BaseModel):
    employee_id: str
    start_date: str
    end_date: str
    leave_type: str
    reason: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "employee_id": "EMP001",
                "start_date": "2024-03-01",
                "end_date": "2024-03-05",
                "leave_type": "Vacation",
                "reason": "Family trip"
            }
        }
    )