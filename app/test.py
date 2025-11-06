import requests
import json
from pprint import pprint

url = " http://localhost:5001/confirm-attendance/af49db6e-ed91-4aed-a63a-4af87dc9282c/verify-otp"

# url = "http://localhost:5000/events"


# payload = {
#     "username": "duckdoe",
#     "title": "Christmas Party",
#     "description": "It's christmas time, a season of love, a season to share. Merry Christmas.",
#     "event_date": "2025-12-25 00:00:00",
# }

payload = {
    # "username": "duckdoe",
    "email": "fortunefoluso23@gmail.com",
    "otp": "95543",
    # "password": "duckdb123",
}


headers = {
    "Content-Type": "application/json",
    "Session-Id": "04843e95-3498-4157-91d2-65df6d107457|admin",
}

res = requests.put(url, data=json.dumps(payload), headers=headers)
# res = requests.get(url)
pprint(res.json())
