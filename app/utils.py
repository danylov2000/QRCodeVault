import hashlib
import jwt
import datetime
import os


def hash_pass(password):
    password = hashlib.sha256(password.encode()).hexdigest()
    return password

def create_access_tokens(full_name, email, user_id):
    now = datetime.datetime.now()
    access_payload = {
        "full_name": full_name,
        "email": email,
        "user_id": user_id,
        "exp": (now + datetime.timedelta(minutes=15)).timestamp(),
        "typ": "access"
    }

    refresh_payload = {
        "user_id": user_id,
        "typ": "refresh",
        "exp": (now + datetime.timedelta(days=1)).timestamp()
    }
    secret = os.environ.get("SECRET_KEY")

    access_token = jwt.encode(access_payload, secret, algorithm="HS256")
    refresh_token = jwt.encode(refresh_payload, secret, algorithm="HS256")

    return access_token, refresh_token
