# src/web_server.py
from fastapi import FastAPI, HTTPException
from typing import Optional, List
import uvicorn
import os
from datetime import date

from .models import Employee, LeaveRequest, LeaveRequestCreate
from .hr_services import hr_db

app = FastAPI(
    title="HR MCP Server",
    description="A Model Context Protocol server for HR services",
    version="1.0.0"
)

@app.get("/")
async def root():
    return {
        "message": "HR MCP Server is running",
        "version": "1.0.0",
        "endpoints": {
            "employees": "/employees",
            "leaves": "/leaves",
            "health": "/health",
            "mcp": "/mcp (SSE endpoint for Copilot)"
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
async def search_employees(
    department: Optional[str] = None,
    name: Optional[str] = None
):
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