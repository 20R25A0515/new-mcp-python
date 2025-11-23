# src/hr_services.py
from typing import Dict, List, Optional
from .models import Employee, LeaveRequest

class HRDatabase:
    def __init__(self):
        self.employees: Dict[str, Employee] = {}
        self.leave_requests: Dict[str, LeaveRequest] = {}
        self._initialize_sample_data()
    
    def _initialize_sample_data(self):
        sample_employees = [
            Employee(
                id="EMP001",
                name="John Doe",
                email="john.doe@company.com",
                department="Engineering",
                position="Software Engineer",
                hire_date="2022-01-15",
                salary=75000.00,
                manager="Jane Smith"
            ),
            Employee(
                id="EMP002",
                name="Jane Smith",
                email="jane.smith@company.com",
                department="Engineering",
                position="Engineering Manager",
                hire_date="2020-03-10",
                salary=95000.00,
                manager="Bob Wilson"
            ),
            Employee(
                id="EMP003",
                name="Alice Johnson",
                email="alice.johnson@company.com",
                department="HR",
                position="HR Specialist",
                hire_date="2021-06-20",
                salary=65000.00,
                manager="Carol Brown"
            )
        ]
        
        for emp in sample_employees:
            self.employees[emp.id] = emp
        
        sample_leaves = [
            LeaveRequest(
                id="LEAVE001",
                employee_id="EMP001",
                start_date="2024-01-10",
                end_date="2024-01-12",
                leave_type="Vacation",
                reason="Family vacation",
                status="approved",
                submitted_date="2023-12-15"
            ),
            LeaveRequest(
                id="LEAVE002",
                employee_id="EMP002",
                start_date="2024-02-01",
                end_date="2024-02-05",
                leave_type="Sick Leave",
                reason="Medical appointment",
                status="pending",
                submitted_date="2024-01-20"
            )
        ]
        
        for leave in sample_leaves:
            self.leave_requests[leave.id] = leave
    
    def get_employee(self, employee_id: str) -> Optional[Employee]:
        return self.employees.get(employee_id)
    
    def get_all_employees(self) -> List[Employee]:
        return list(self.employees.values())
    
    def search_employees(self, department: Optional[str] = None, name: Optional[str] = None) -> List[Employee]:
        results = self.employees.values()
        if department:
            results = [emp for emp in results if department.lower() in emp.department.lower()]
        if name:
            results = [emp for emp in results if name.lower() in emp.name.lower()]
        return list(results)
    
    def get_employee_leaves(self, employee_id: str) -> List[LeaveRequest]:
        return [leave for leave in self.leave_requests.values() if leave.employee_id == employee_id]
    
    def get_all_leaves(self, status: Optional[str] = None) -> List[LeaveRequest]:
        results = self.leave_requests.values()
        if status:
            results = [leave for leave in results if leave.status.lower() == status.lower()]
        return list(results)
    
    def create_leave_request(self, leave_data: dict) -> LeaveRequest:
        leave_id = f"LEAVE{len(self.leave_requests) + 1:03d}"
        leave = LeaveRequest(id=leave_id, **leave_data)
        self.leave_requests[leave_id] = leave
        return leave

# Global instance
hr_db = HRDatabase()