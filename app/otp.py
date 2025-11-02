import hmac
import pyotp
import base64
import hashlib
import smtplib
import secrets
from email.mime.text import MIMEText


secret_key = secrets.token_urlsafe(32)


def generate(email):
    h = hmac.new(secret_key.encode(), email.encode(), hashlib.sha256)
    digest = h.digest()
    user_secret = base64.b32encode(digest).decode("utf-8")
    totp = pyotp.TOTP(user_secret, digits=5, interval=300)

    otp = totp.now()
    return otp


def verify_otp(email, otp):
    h = hmac.new(secret_key.encode(), email.encode(), hashlib.sha256)
    digest = h.digest()
    user_secret = base64.b32encode(digest).decode("utf-8")
    totp = pyotp.TOTP(user_secret, digits=5, interval=120)

    return totp.verify(email, otp)


email = "fortunefoluso@gmail.com"

otp = generate(email)
print(otp)

otp_is_same = verify_otp(email, otp)
print(otp_is_same)


def send_otp_email(email, otp):
    body = f"This is your otp {otp} Dont share with anyone"
    message = MIMEText(body)
    message["Subject"] = "Otp"
    message["From"] = "fortunefoluso@gmail.com"
    message["To"] = email

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login("fortunefoluso@gmail.com", "mvnc vewx phte egyj")
        server.sendmail(message["From"], message["To"], message.as_string())


send_otp_email("fortunefoluso@gmail.com", otp)
