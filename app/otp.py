import os
import hmac
import pyotp
import base64
import hashlib
import smtplib
import secrets
import requests
from datetime import datetime
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")


secret_key = secrets.token_urlsafe(32)


def generate(email):
    """
    Utility function to generate a new otp using the users secrets and the apps secrets

    :params: email: str

    :returns: int
    """
    h = hmac.new(secret_key.encode(), email.encode(), hashlib.sha256)
    digest = h.digest()
    user_secret = base64.b32encode(digest).decode("utf-8")
    totp = pyotp.TOTP(
        user_secret, digits=5, interval=120
    )  # Regenerate a new otp every 2 min

    otp = totp.now()
    return otp


def verify_otp(email, otp):
    """
    Utility function to verify the otp provided

    :params: email: str
    :params: otp: int

    :returns: bool
    """
    h = hmac.new(secret_key.encode(), email.encode(), hashlib.sha256)
    digest = h.digest()
    user_secret = base64.b32encode(digest).decode("utf-8")
    totp = pyotp.TOTP(user_secret, digits=5, interval=120)

    return totp.verify(otp)


email = "fortunefoluso@gmail.com"


def send_otp_email(email, otp):
    """
    Utility function to send the otp generated to the provided email

    :params: email: str
    :params: otp: int

    :returns: None
    """
    body = f"This is your otp {otp}. Dont share with anyone. Your OTP will last for only two minutes."
    message = MIMEText(body)
    message["Subject"] = "Otp"
    message["From"] = SENDER_EMAIL
    message["To"] = email

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(message["From"], message["To"], message.as_string())


def send_email(email, body, subject):
    message = MIMEText(body)
    message["Subject"] = subject
    message["From"] = "fortunefoluso@gmail.com"
    message["To"] = email

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login("fortunefoluso@gmail.com", "mvnc vewx phte egyj")
        server.sendmail(message["From"], message["To"], message.as_string())

    return True


def get_address(ip):
    url = f"https://ipapi.co/{ip}/json"
    res = requests.get(url)

    if res.status_code != 200:
        return None

    res = res.json()

    city = res.get("city")
    region = res.get("region")
    country = res.get("country_name")

    address = f"Near {city}, {region}, {country}"

    return address


# send_otp_email("fortunefoluso@gmail.com", otp)
def send_login_alert(email, ip):
    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    address = get_address(ip)

    body = f"A new login was detected on your account from {address} at {timestamp}"
    subject = "Login Alert Notification"

    send_email(email, body, subject)


def send_registration_email(email, user, event):
    body = f"{user} just registered for {event} event."
    subject = "Registered for event"

    send_email(email, body, subject)
