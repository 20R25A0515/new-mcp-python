# src/models_simple.py - Fallback without Pydantic
from typing import Dict, List, Optional, Any

class Employee:
    def __init__(self, id: str, name: str, email: str, department: str, position: str, 
                 hire_date: str, salary: Optional[float] = None, manager: Optional[str] = None):
        self.id = id
        self.name = name
        self.email = email
        self.department = department
        self.position = position
        self.hire_date = hire_date
        self.salary = salary
        self.manager = manager
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "department": self.department,
            "position": self.position,
            "hire_date": self.hire_date,
            "salary": self.salary,
            "manager": self.manager
        }