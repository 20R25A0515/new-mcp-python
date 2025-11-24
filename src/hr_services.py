# src/hr_services.py
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
    
    def to_dict(self):
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
    
    def to_dict(self):
        return {
            "id": self.id,
            "employee_id": self.employee_id,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "leave_type": self.leave_type,
            "reason": self.reason,
            "status": self.status,
            "submitted_date": self.submitted_date
        }

class HRDatabase:
    def __init__(self):
        self.employees = {}
        self.leave_requests = {}
        self._initialize_sample_data()
    
    def _initialize_sample_data(self):
        # Sample employees
        sample_employees = [
            Employee("EMP001", "John Doe", "john.doe@company.com", "Engineering", "Software Engineer", "2022-01-15", 75000.00, "Jane Smith"),
            Employee("EMP002", "Jane Smith", "jane.smith@company.com", "Engineering", "Engineering Manager", "2020-03-10", 95000.00, "Bob Wilson"),
            Employee("EMP003", "Alice Johnson", "alice.johnson@company.com", "HR", "HR Specialist", "2021-06-20", 65000.00, "Carol Brown")
        ]
        
        for emp in sample_employees:
            self.employees[emp.id] = emp
        
        # Sample leave requests
        sample_leaves = [
            LeaveRequest("LEAVE001", "EMP001", "2024-01-10", "2024-01-12", "Vacation", "Family vacation", "approved", "2023-12-15"),
            LeaveRequest("LEAVE002", "EMP002", "2024-02-01", "2024-02-05", "Sick Leave", "Medical appointment", "pending", "2024-01-20")
        ]
        
        for leave in sample_leaves:
            self.leave_requests[leave.id] = leave
    
    def get_employee(self, employee_id):
        emp = self.employees.get(employee_id)
        return emp.to_dict() if emp else None
    
    def get_all_employees(self):
        return [emp.to_dict() for emp in self.employees.values()]
    
    def search_employees(self, department=None, name=None):
        results = list(self.employees.values())
        if department:
            results = [emp for emp in results if department.lower() in emp.department.lower()]
        if name:
            results = [emp for emp in results if name.lower() in emp.name.lower()]
        return [emp.to_dict() for emp in results]
    
    def get_employee_leaves(self, employee_id):
        leaves = [leave for leave in self.leave_requests.values() if leave.employee_id == employee_id]
        return [leave.to_dict() for leave in leaves]
    
    def get_all_leaves(self, status=None):
        results = list(self.leave_requests.values())
        if status:
            results = [leave for leave in results if leave.status.lower() == status.lower()]
        return [leave.to_dict() for leave in results]
    
    def create_leave_request(self, leave_data):
        leave_id = f"LEAVE{len(self.leave_requests) + 1:03d}"
        leave = LeaveRequest(
            id=leave_id,
            employee_id=leave_data["employee_id"],
            start_date=leave_data["start_date"],
            end_date=leave_data["end_date"],
            leave_type=leave_data["leave_type"],
            reason=leave_data["reason"],
            status=leave_data["status"],
            submitted_date=leave_data["submitted_date"]
        )
        self.leave_requests[leave_id] = leave
        return leave.to_dict()

# Global instance
hr_db = HRDatabase()