import requests
import json
from pprint import pprint

url = "http://localhost:5000/register/e6359998-3790-452d-bcef-4e6cd33f87b7"

# url = "http://localhost:5000/events"


# payload = {
#     "username": "duckdoe",
#     "title": "Christmas Party",
#     "description": "It's christmas time, a season of love, a season to share. Merry Christmas.",
#     "event_date": "2025-12-25 00:00:00",
# }

payload = {
    "username": "duckdoe",
    # "email": "fortunefoluso23@gmail.com",
    # "password": "duckdb123",
}

headers = {
    "Content-Type": "application/json",
    "Session-Id": "d597b1f2-d4b6-4ac8-a417-fe3aeb15f318|user",
}

res = requests.post(url, data=json.dumps(payload), headers=headers)
# res = requests.get(url)
pprint(res.json())
