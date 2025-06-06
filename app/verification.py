import os
import smtplib
import uuid
from email.message import EmailMessage

HOST = os.environ.get("SMTP_HOST")
USERNAME = os.environ.get("SMTP_USERNAME")
PASSWORD = os.environ.get("SMTP_PASSWORD")
PORT = os.environ.get("SMTP_PORT")


class SmtpVerifier:

    def __init__(self):
        self.active_verifications = {}
        self.connection = smtplib.SMTP_SSL(HOST, int(PORT))
        self.connection.login(USERNAME, PASSWORD)

    def create_ver_code(self, user_id):
        code = uuid.uuid4().hex
        self.active_verifications[code] = user_id
        return code

    def verify(self, code):
        if code in self.active_verifications:
            self.active_verifications.pop(code)
            return True
        return False

    def send_confirmation_email(self, recipient, user_id):

        code = self.create_ver_code(user_id)
        url = f"http://127.0.0.1:8000/auth/verify?code={code}"

        msg = EmailMessage()
        msg["Subject"] = "Email Confirmation"
        msg["From"] = USERNAME
        msg["To"] = recipient
        msg.set_content(f"Click the url to verify your account: {url}")
        self.connection.send_message(msg)
