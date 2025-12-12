import requests

url = "http://127.0.0.1:5000/auth/register"
payload = {
    "username": "py_test_user",
    "password": "mypassword123"
}

response = requests.post(url, json=payload)

print("Status Code:", response.status_code)
print("Response:", response.json())
