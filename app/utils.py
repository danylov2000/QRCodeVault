import hashlib
import urllib

import jwt
import datetime
import os
import logging
import urllib.parse
import requests
from jwt import ExpiredSignatureError, InvalidTokenError

logger = logging.getLogger(__name__)

params = {
    "client_id": os.environ.get("GOOGLE_OAUTH_CLIENT_ID"),
    "redirect_uri": os.environ.get("GOOGLE_OAUTH_URI"),
    "response_type": "code",
    "scope": "https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile"
}
google_auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urllib.parse.urlencode(params)}"

token_url = "https://oauth2.googleapis.com/token"

user_info_url = "https://www.googleapis.com/oauth2/v3/userinfo"

def hash_pass(password):
    logger.debug("Hashing password")
    password = hashlib.sha256(password.encode()).hexdigest()
    return password

def create_access_tokens(full_name, email, user_id):
    logger.debug(f"Creating access and refresh tokens for user_id={user_id}, email={email}")

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

    try:
        access_token = jwt.encode(access_payload, secret, algorithm="HS256")
        refresh_token = jwt.encode(refresh_payload, secret, algorithm="HS256")
    except Exception as e:
        logger.exception(f"Error while encoding JWT tokens for user_id={user_id}")
        raise

    logger.info(f"JWT tokens successfully created for user_id={user_id}")

    return access_token, refresh_token


def validate_token(token):
    secret = os.environ.get("SECRET_KEY")

    try:
        payload = jwt.decode(token, secret, algorithms=["HS256"])
        return payload
    except ExpiredSignatureError:
        logger.info("Token expired")

    except InvalidTokenError:
        logger.info("Token not valid")


def google_oauth_code_exchange(code):
    payload = {
        "code": code,
        "client_id": os.environ.get("GOOGLE_OAUTH_CLIENT_ID"),
        "client_secret": os.environ.get("GOOGLE_OAUTH_SECRET"),
        "grant_type": "authorization_code",
        "redirect_uri": os.environ.get("GOOGLE_OAUTH_URI")
    }

    response = requests.post(token_url, data=payload)
    tokens = response.json()

    if "access_token" not in tokens:
        logger.error(f"Google OAuth failed: {tokens}")
        return "OAuth failed", 400

    access_token = tokens["access_token"]
    user_response = requests.get(
    user_info_url,
        headers={"Authorization": f"Bearer {access_token}"}
    )
    user_info = user_response.json()
    return user_info

