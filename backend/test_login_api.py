import requests

url = "http://localhost:5000/api/auth/login"
payload = {
    "employee_id": "ADMIN-001",
    "password": "admin@123"
}

try:
    response = requests.post(url, json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")
