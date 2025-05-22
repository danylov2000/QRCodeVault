import hashlib
import jwt
import datetime
import os
import logging

from jwt import ExpiredSignatureError, InvalidTokenError

logger = logging.getLogger(__name__)


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



