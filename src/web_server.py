# src/web_server.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import uvicorn
import os
from datetime import date

# Use the same HR database classes from mcp_server.py
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

class HRDatabase:
    def __init__(self):
        self.employees = {}
        self.leave_requests = {}
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
    
    def get_employee(self, employee_id):
        return self.employees.get(employee_id)
    
    def get_all_employees(self):
        return list(self.employees.values())
    
    def search_employees(self, department=None, name=None):
        results = self.employees.values()
        if department:
            results = [emp for emp in results if department.lower() in emp.department.lower()]
        if name:
            results = [emp for emp in results if name.lower() in emp.name.lower()]
        return list(results)
    
    def get_employee_leaves(self, employee_id):
        return [leave for leave in self.leave_requests.values() if leave.employee_id == employee_id]
    
    def get_all_leaves(self, status=None):
        results = self.leave_requests.values()
        if status:
            results = [leave for leave in results if leave.status.lower() == status.lower()]
        return list(results)
    
    def create_leave_request(self, leave_data):
        leave_id = f"LEAVE{len(self.leave_requests) + 1:03d}"
        leave = LeaveRequest(id=leave_id, **leave_data)
        self.leave_requests[leave_id] = leave
        return leave

# Initialize database
hr_db = HRDatabase()

# FastAPI app
app = FastAPI(
    title="HR MCP Server",
    description="A Model Context Protocol server for HR services",
    version="1.0.0"
)

class LeaveRequestCreate(BaseModel):
    employee_id: str
    start_date: str
    end_date: str
    leave_type: str
    reason: str

@app.get("/")
async def root():
    return {
        "message": "HR MCP Server is running",
        "version": "1.0.0",
        "endpoints": {
            "employees": "/employees",
            "leaves": "/leaves",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/employees", response_model=List[Employee])
async def get_all_employees():
    return hr_db.get_all_employees()

@app.get("/employees/{employee_id}", response_model=Employee)
async def get_employee(employee_id: str):
    employee = hr_db.get_employee(employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee

@app.get("/employees/search/")
async def search_employees(department: Optional[str] = None, name: Optional[str] = None):
    return hr_db.search_employees(department, name)

@app.get("/leaves", response_model=List[LeaveRequest])
async def get_all_leaves(status: Optional[str] = None):
    return hr_db.get_all_leaves(status)

@app.get("/leaves/employee/{employee_id}", response_model=List[LeaveRequest])
async def get_employee_leaves(employee_id: str):
    employee = hr_db.get_employee(employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return hr_db.get_employee_leaves(employee_id)

@app.post("/leaves", response_model=LeaveRequest)
async def create_leave_request(leave_data: LeaveRequestCreate):
    employee = hr_db.get_employee(leave_data.employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    leave_dict = leave_data.dict()
    leave_dict.update({
        "status": "pending",
        "submitted_date": str(date.today())
    })
    
    leave = hr_db.create_leave_request(leave_dict)
    return leave

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)