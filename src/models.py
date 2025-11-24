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