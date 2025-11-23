# 1src/web_server.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import uvicorn
import os

from .hr_services import hr_db, Employee, LeaveRequest

app = FastAPI(
    title="HR MCP Server",
    description="A Model Context Protocol server for HR services",
    version="1.0.0"
)

# Pydantic models for API
class EmployeeResponse(BaseModel):
    id: str
    name: str
    email: str
    department: str
    position: str
    hire_date: str
    salary: Optional[float] = None
    manager: Optional[str] = None

class LeaveRequestCreate(BaseModel):
    employee_id: str
    start_date: str
    end_date: str
    leave_type: str
    reason: str

class LeaveRequestResponse(BaseModel):
    id: str
    employee_id: str
    start_date: str
    end_date: str
    leave_type: str
    reason: str
    status: str
    submitted_date: str

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

@app.get("/employees", response_model=List[EmployeeResponse])
async def get_all_employees():
    """Get all employees"""
    return hr_db.get_all_employees()

@app.get("/employees/{employee_id}", response_model=EmployeeResponse)
async def get_employee(employee_id: str):
    """Get employee by ID"""
    employee = hr_db.get_employee(employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee

@app.get("/employees/search/")
async def search_employees(
    department: Optional[str] = None,
    name: Optional[str] = None
):
    """Search employees by department or name"""
    return hr_db.search_employees(department, name)

@app.get("/leaves", response_model=List[LeaveRequestResponse])
async def get_all_leaves(status: Optional[str] = None):
    """Get all leave requests with optional status filter"""
    return hr_db.get_all_leaves(status)

@app.get("/leaves/employee/{employee_id}", response_model=List[LeaveRequestResponse])
async def get_employee_leaves(employee_id: str):
    """Get leave requests for a specific employee"""
    employee = hr_db.get_employee(employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return hr_db.get_employee_leaves(employee_id)

@app.post("/leaves", response_model=LeaveRequestResponse)
async def create_leave_request(leave_data: LeaveRequestCreate):
    """Create a new leave request"""
    employee = hr_db.get_employee(leave_data.employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    leave_dict = leave_data.dict()
    leave_dict.update({
        "status": "pending",
        "submitted_date": str(__import__('datetime').date.today())
    })
    
    leave = hr_db.create_leave_request(leave_dict)
    return leave

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)