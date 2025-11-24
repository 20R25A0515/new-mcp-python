import requests
import json

BASE_URL = "https://your-render-url.onrender.com"

def test_endpoint(endpoint):
    try:
        response = requests.get(f"{BASE_URL}{endpoint}")
        print(f"GET {endpoint}: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(json.dumps(data, indent=2))
        else:
            print(f"Error: {response.text}")
        print("-" * 50)
    except Exception as e:
        print(f"Error testing {endpoint}: {e}")

def main():
    print("Testing HR MCP Server API...\n")
    
    endpoints = [
        "/",
        "/health",
        "/employees", 
        "/employees/EMP001",
        "/employees/search/?department=Engineering",
        "/leaves",
        "/leaves/employee/EMP001"
    ]
    
    for endpoint in endpoints:
        test_endpoint(endpoint)

if __name__ == "__main__":
    main()