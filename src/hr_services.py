# src/mcp_server.py
import asyncio
import sys
import os
from datetime import date

# Use the correct imports based on your MCP package
from mcp.server import Server
from mcp.server.models import InitializationOptions
import mcp.server.stdio
from mcp.types import Tool, TextContent, Resource

# HR Database (same as before)
class Employee:
    def __init__(self, id, name, email, department, position, hire_date, salary=None, manager=None):
        self.id = id
        self.name = name
        self.email = email
        self.department = department
        self.position = position
        self.hire_date = hire_date
        self.salary = salary
        self.manager = manager

class LeaveRequest:
    def __init__(self, id, employee_id, start_date, end_date, leave_type, reason, status, submitted_date):
        self.id = id
        self.employee_id = employee_id
        self.start_date = start_date
        self.end_date = end_date
        self.leave_type = leave_type
        self.reason = reason
        self.status = status
        self.submitted_date = submitted_date

class HRDatabase:
    def __init__(self):
        self.employees = {}
        self.leave_requests = {}
        self._initialize_sample_data()
    
    def _initialize_sample_data(self):
        # Sample employees
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
        
        # Sample leave requests
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

# Create MCP server instance
app = Server("hr-mcp-server")

@app.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available HR tools"""
    return [
        Tool(
            name="get_employee_details",
            description="Get detailed information about a specific employee by their ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "employee_id": {
                        "type": "string",
                        "description": "The unique ID of the employee"
                    }
                },
                "required": ["employee_id"]
            }
        ),
        Tool(
            name="get_all_employees",
            description="Get list of all employees in the company",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="search_employees",
            description="Search employees by department or name",
            inputSchema={
                "type": "object",
                "properties": {
                    "department": {
                        "type": "string",
                        "description": "Department to filter by (optional)"
                    },
                    "name": {
                        "type": "string",
                        "description": "Name to search for (optional)"
                    }
                }
            }
        ),
        Tool(
            name="get_employee_leave_requests",
            description="Get all leave requests for a specific employee",
            inputSchema={
                "type": "object",
                "properties": {
                    "employee_id": {
                        "type": "string",
                        "description": "The unique ID of the employee"
                    }
                },
                "required": ["employee_id"]
            }
        ),
        Tool(
            name="get_all_leave_requests",
            description="Get all leave requests with optional status filter",
            inputSchema={
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "description": "Filter by status: pending, approved, or rejected (optional)"
                    }
                }
            }
        ),
        Tool(
            name="create_leave_request",
            description="Create a new leave request for an employee",
            inputSchema={
                "type": "object",
                "properties": {
                    "employee_id": {
                        "type": "string",
                        "description": "The unique ID of the employee"
                    },
                    "start_date": {
                        "type": "string",
                        "description": "Start date of leave (YYYY-MM-DD)"
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date of leave (YYYY-MM-DD)"
                    },
                    "leave_type": {
                        "type": "string",
                        "description": "Type of leave: Vacation, Sick Leave, Personal, etc."
                    },
                    "reason": {
                        "type": "string",
                        "description": "Reason for the leave request"
                    }
                },
                "required": ["employee_id", "start_date", "end_date", "leave_type", "reason"]
            }
        )
    ]

@app.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool execution"""
    try:
        if name == "get_employee_details":
            employee_id = arguments["employee_id"]
            employee = hr_db.get_employee(employee_id)
            if not employee:
                return [TextContent(type="text", text=f"Employee with ID {employee_id} not found")]
            
            return [TextContent(
                type="text",
                text=f"Employee Details:\n"
                     f"ID: {employee.id}\n"
                     f"Name: {employee.name}\n"
                     f"Email: {employee.email}\n"
                     f"Department: {employee.department}\n"
                     f"Position: {employee.position}\n"
                     f"Hire Date: {employee.hire_date}\n"
                     f"Salary: ${employee.salary:,.2f}\n"
                     f"Manager: {employee.manager or 'N/A'}"
            )]
        
        elif name == "get_all_employees":
            employees = hr_db.get_all_employees()
            if not employees:
                return [TextContent(type="text", text="No employees found")]
            
            employee_list = "\n\n".join([
                f"ID: {emp.id}, Name: {emp.name}, Department: {emp.department}, Position: {emp.position}"
                for emp in employees
            ])
            return [TextContent(
                type="text",
                text=f"Total Employees: {len(employees)}\n\n{employee_list}"
            )]
        
        elif name == "search_employees":
            department = arguments.get("department")
            name_filter = arguments.get("name")
            
            employees = hr_db.search_employees(department, name_filter)
            if not employees:
                filters = []
                if department: filters.append(f"department: {department}")
                if name_filter: filters.append(f"name: {name_filter}")
                filter_text = " with " + " and ".join(filters) if filters else ""
                return [TextContent(type="text", text=f"No employees found{filter_text}")]
            
            employee_list = "\n\n".join([
                f"ID: {emp.id}, Name: {emp.name}, Department: {emp.department}, Position: {emp.position}"
                for emp in employees
            ])
            
            filters = []
            if department: filters.append(f"department: {department}")
            if name_filter: filters.append(f"name: {name_filter}")
            filter_text = " with " + " and ".join(filters) if filters else ""
            
            return [TextContent(
                type="text",
                text=f"Found {len(employees)} employees{filter_text}:\n\n{employee_list}"
            )]
        
        elif name == "get_employee_leave_requests":
            employee_id = arguments["employee_id"]
            leaves = hr_db.get_employee_leaves(employee_id)
            employee = hr_db.get_employee(employee_id)
            
            if not employee:
                return [TextContent(type="text", text=f"Employee with ID {employee_id} not found")]
            
            if not leaves:
                return [TextContent(
                    type="text",
                    text=f"No leave requests found for employee {employee.name} (ID: {employee_id})"
                )]
            
            leave_list = "\n\n".join([
                f"Leave ID: {leave.id}\n"
                f"Period: {leave.start_date} to {leave.end_date}\n"
                f"Type: {leave.leave_type}\n"
                f"Reason: {leave.reason}\n"
                f"Status: {leave.status}\n"
                f"Submitted: {leave.submitted_date}"
                for leave in leaves
            ])
            
            return [TextContent(
                type="text",
                text=f"Leave requests for {employee.name} (ID: {employee_id}):\n\n{leave_list}"
            )]
        
        elif name == "get_all_leave_requests":
            status = arguments.get("status")
            leaves = hr_db.get_all_leaves(status)
            
            if not leaves:
                status_text = f" with status '{status}'" if status else ""
                return [TextContent(type="text", text=f"No leave requests found{status_text}")]
            
            leave_list = "\n\n".join([
                f"Leave ID: {leave.id}\n"
                f"Employee ID: {leave.employee_id}\n"
                f"Period: {leave.start_date} to {leave.end_date}\n"
                f"Type: {leave.leave_type}\n"
                f"Status: {leave.status}\n"
                f"Submitted: {leave.submitted_date}"
                for leave in leaves
            ])
            
            status_text = f" with status '{status}'" if status else ""
            return [TextContent(
                type="text",
                text=f"All leave requests{status_text}:\n\n{leave_list}"
            )]
        
        elif name == "create_leave_request":
            leave_data = {
                "employee_id": arguments["employee_id"],
                "start_date": arguments["start_date"],
                "end_date": arguments["end_date"],
                "leave_type": arguments["leave_type"],
                "reason": arguments["reason"],
                "status": "pending",
                "submitted_date": str(date.today())
            }
            
            employee = hr_db.get_employee(leave_data["employee_id"])
            if not employee:
                return [TextContent(type="text", text=f"Employee with ID {leave_data['employee_id']} not found")]
            
            leave = hr_db.create_leave_request(leave_data)
            
            return [TextContent(
                type="text",
                text=f"Leave request created successfully!\n\n"
                     f"Leave ID: {leave.id}\n"
                     f"Employee: {employee.name} (ID: {employee.id})\n"
                     f"Period: {leave.start_date} to {leave.end_date}\n"
                     f"Type: {leave.leave_type}\n"
                     f"Reason: {leave.reason}\n"
                     f"Status: {leave.status}\n"
                     f"Submitted Date: {leave.submitted_date}"
            )]
        
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
    
    except Exception as e:
        return [TextContent(type="text", text=f"Error executing tool {name}: {str(e)}")]

@app.list_resources()
async def handle_list_resources() -> list[Resource]:
    """List available resources"""
    return [
        Resource(
            uri="hr://employees/summary",
            name="Employees Summary",
            description="Summary of all employees in the organization",
            mimeType="text/plain"
        ),
        Resource(
            uri="hr://leaves/summary",
            name="Leaves Summary", 
            description="Summary of all leave requests",
            mimeType="text/plain"
        )
    ]

@app.read_resource()
async def handle_read_resource(uri: str) -> str:
    """Handle resource reading"""
    if uri == "hr://employees/summary":
        employees = hr_db.get_all_employees()
        dept_counts = {}
        for emp in employees:
            dept_counts[emp.department] = dept_counts.get(emp.department, 0) + 1
        
        summary = f"HR Employees Summary\n{'='*20}\n"
        summary += f"Total Employees: {len(employees)}\n\n"
        summary += "Department Breakdown:\n"
        for dept, count in dept_counts.items():
            summary += f"- {dept}: {count} employees\n"
        
        return summary
    
    elif uri == "hr://leaves/summary":
        leaves = hr_db.get_all_leaves()
        status_counts = {}
        type_counts = {}
        
        for leave in leaves:
            status_counts[leave.status] = status_counts.get(leave.status, 0) + 1
            type_counts[leave.leave_type] = type_counts.get(leave.leave_type, 0) + 1
        
        summary = f"HR Leaves Summary\n{'='*20}\n"
        summary += f"Total Leave Requests: {len(leaves)}\n\n"
        summary += "Status Breakdown:\n"
        for status, count in status_counts.items():
            summary += f"- {status.title()}: {count}\n"
        
        summary += "\nType Breakdown:\n"
        for leave_type, count in type_counts.items():
            summary += f"- {leave_type}: {count}\n"
        
        return summary
    
    else:
        raise ValueError(f"Unknown resource: {uri}")

async def main():
    # Run the server using stdio
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="hr-mcp-server",
                server_version="1.0.0"
            )
        )

if __name__ == "__main__":
    asyncio.run(main())