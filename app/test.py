import requests
import json
from pprint import pprint

url = " http://localhost:5000/register/c2e689c5-c5cd-4de9-88e3-bf99b1f40a85"

# url = "http://localhost:5000/events"

payload = {
    "username": "duckdbuser",
    "password": "duckdb123",
}

# payload = {
#     "username": "duckdoe",
#     "title": "Christmas Party",
#     "description": "It's christmas time, a season of love, a season to share. Merry Christmas.",
#     "event_date": "2025-12-25 00:00:00",
# }

payload = {
    "username": "duckuser",
    "email": "fortunefoluso23@gmail.com",
}


headers = {
    "Content-Type": "application/json",
    "Session-Id": "8954bc3a-f838-4e7f-a6e7-8a220e08020f|admin",
}

res = requests.post(url, data=json.dumps(payload), headers=headers)
# res = requests.get(url)
pprint(res.json())
