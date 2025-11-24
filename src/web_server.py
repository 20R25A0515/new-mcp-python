# src/web_server.py
from flask import Flask, request, jsonify
import os
import sys

# Fix imports
sys.path.append(os.path.dirname(__file__))

try:
    from hr_services import hr_db
except ImportError:
    from .hr_services import hr_db

app = Flask(__name__)

@app.route("/")
def root():
    return jsonify({
        "message": "HR REST API Server",
        "version": "1.0.0"
    })

@app.route("/employees", methods=["GET"])
def get_all_employees():
    return jsonify(hr_db.get_all_employees())

@app.route("/employees/<employee_id>", methods=["GET"])
def get_employee(employee_id):
    employee = hr_db.get_employee(employee_id)
    if not employee:
        return jsonify({"error": "Employee not found"}), 404
    return jsonify(employee)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8001))
    app.run(host="0.0.0.0", port=port)