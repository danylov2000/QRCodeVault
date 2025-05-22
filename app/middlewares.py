from flask import request
import os
import jwt
from jwt import ExpiredSignatureError, InvalidTokenError
import logging
from app.utils import validate_token

from flask import redirect

logger = logging.getLogger(__name__)


def auth_required(handler):
    def wrapper(*args, **kwargs):
        access_token = request.cookies.get("access")

        payload = validate_token(access_token)
        if payload:
            logger.info("Valid token: access granted")
            return handler(payload, *args, **kwargs)
        else:
            logger.info("Non-Valid token")
            return redirect("/auth/sign-in")

    return wrapper
