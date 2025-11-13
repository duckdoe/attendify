import requests
import json
from pprint import pprint

# url = " http://localhost:5000/login"
url = "http://localhost:5000/confirm-attendance/dc1629cc-75e6-44f1-8c53-70777570248e/upload"

# url = "http://localhost:5000/events"

# payload = {
#     "username": "duckdoe",
#     "title": "Christmas Party",
#     "description": "It's christmas time, a season of love, a season to share. Merry Christmas.",
#     "event_date": "2025-12-25 00:00:00",
# }

document = r"C:\Users\duck\Downloads\attendify_detailed_prd.pdf"
image = r"C:\Users\duck\Downloads\Fortune_web.png"


with open(document, "rb") as doc, open(image, "rb") as img:
    files = {
        "document": ("document.pdf", doc, "application/pdf"),
        "image": ("image.png", img, "image/png"),
    }

    payload = {"email": "fortuneweb11@gmail.com"}
    headers = {
        "Session-Id": "d07144db-84c8-4182-b456-2c450acc9732|user",
    }

    res = requests.post(url, data=payload, headers=headers, files=files)
    # res = requests.get(url)
    pprint(res.json())


# payload = {"username": "fortune", "password": "fortune123"}

# headers = {"Content-Type": "application/json", }

# res = requests.post(url, data=json.dumps(payload), headers=headers)
# pprint(res.json())
