import os
from app.utils import validate_token
import jwt
from flask import Blueprint, render_template, request, jsonify, redirect
from jwt import ExpiredSignatureError, InvalidTokenError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.utils import hash_pass, create_access_tokens
from app.database.models import User
from app.database import session
import logging

logger = logging.getLogger(__name__)

router = Blueprint("auth", __name__)


@router.get("/sign-in")
def sign_in_handler():
    logger.info("Sign-in page requested")
    refresh_token = request.cookies.get("refresh")
    payload = validate_token(refresh_token)

    if payload:
        user = session.query(User).get(payload.get("user_id"))
        access_token, refresh_token = create_access_tokens(
            full_name=f"{user.first_name} {user.last_name}",
            email=user.email,
            user_id=user.id
        )

        response = redirect("/account")

        response.set_cookie("access", access_token, max_age=60 * 15)
        response.set_cookie("refresh", refresh_token, max_age=60 * 60 * 24)
        return response

    return render_template("signin.html")


@router.get("/sign-up")
def sign_up_handler():
    logger.info("Sign-up page requested")
    return render_template("signup.html")


@router.post("/sign-up/submit")
def sign_up_sub_handler():
    data = request.form
    first_name = data.get("firstName")
    last_name = data.get("lastName")
    phone_number = data.get("phone")
    email = data.get("email")
    password = data.get("password")

    logger.info(f"Attempting sign-up for email: {email}")

    hashed_password = hash_pass(password)

    user = User(first_name, last_name, phone_number, email, hashed_password)
    try:
        session.add(user)
        session.commit()
        logger.info(f"User created: {email}")
        return redirect("/auth/sign-in")
    except IntegrityError:
        session.rollback()
        logger.warning(f"User already exists: {email}")
        return "error, user exists"
    except SQLAlchemyError as e:
        session.rollback()
        logger.exception(f"Unexpected DB error during sign-up for {email}: {e}")
        return "Internal Server Error"


@router.post("/sign-in/submit")
def sign_in_sub_handler():
    email = request.form.get("email")
    password = request.form.get("password")

    logger.info(f"Login attempt for email: {email}")

    hashed_password = hash_pass(password)

    try:
        user = session.query(User).where(User.email == email).where(User.password == hashed_password).one_or_none()

        if not user:
            logger.warning(f"Login failed for email: {email}")
            return redirect("/auth/sign-up")
        else:

            access_token, refresh_token = create_access_tokens(
                full_name=f"{user.first_name} {user.last_name}",
                email=user.email,
                user_id=user.id
            )

            response = redirect("/account")

            response.set_cookie("access", access_token, max_age=60 * 15)
            response.set_cookie("refresh", refresh_token, max_age=60 * 60 * 24)

            logger.info(f"Login successful for user: {user.email}")
            logger.info("Redirecting to account")
            return response

    except SQLAlchemyError as e:
        logger.exception(f"Unexpected DB error during login for {email}: {e}")
        return "Internal Server Error"
