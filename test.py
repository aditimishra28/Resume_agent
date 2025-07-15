import requests

API_URL = "hf_XXXXXXXXXXXXXXXXXXXXXXXXXX"

headers = {"Authorization": "Bearer hf_XXXXXXXXXXXXXXXXXXXXXXXXXX"}


response = requests.post(
    API_URL,
    headers=headers,
    json={"inputs": "Say hello!"},
    timeout=60
)
print(response.status_code)
print(response.text)
