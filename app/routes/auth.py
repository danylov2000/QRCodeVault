import uuid

from faker import Faker

from app.utils import validate_token, google_oauth_code_exchange, google_auth_url
import jwt
from flask import Blueprint, render_template, request, jsonify, redirect
from jwt import ExpiredSignatureError, InvalidTokenError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.utils import hash_pass, create_access_tokens
from app.database.models import User
from app.database import session
import logging
import requests
from app.verification import SmtpVerifier

faker = Faker()

logger = logging.getLogger(__name__)

router = Blueprint("auth", __name__)

verifier = SmtpVerifier()


@router.get("/oauth/google")
def google_oauth_handler():
    code = request.args.get("code")
    if not code:
        logger.warning("No code provided in Google OAuth callback.")
        return "Authorization code missing", 400

    logger.info("Received OAuth code, exchanging for tokens.")
    user_info = google_oauth_code_exchange(code)
    try:

        logger.info(f"Google user info retrieved: {user_info.get('email')}")

        user = session.query(User).filter_by(email=user_info["email"]).first()

        if not user:
            user = User(
                first_name=user_info["given_name"],
                last_name=user_info["family_name"],
                email=user_info["email"],
                is_verified = True
            )

            session.add(user)
            session.commit()
            logger.info(f"Successfully created user account for: {user_info['email']}")


        else:
            logger.info(f"User already exists: {user_info['email']}")
        access_token, refresh_token = create_access_tokens(
            full_name=f"{user.first_name} {user.last_name}",
            email=user.email,
            user_id=user.id
        )

        response = redirect("/account")

        response.set_cookie("access", access_token, max_age=60 * 15)
        response.set_cookie("refresh", refresh_token, max_age=60 * 60 * 24)

        return response


    except IntegrityError:
        session.rollback()
        logger.warning(f"Sign-up failed: user with email {user_info['email']} already exists.")
        return "error, user exists"
    except SQLAlchemyError as e:
        session.rollback()
        logger.exception(f"Unexpected DB error during sign-up for {user_info['email']}: {e}")
        return "Internal Server Error"


@router.get("/logout")
def logout_handler():
    response = redirect("/")
    response.set_cookie("access", "")
    response.set_cookie("refresh", "")
    logger.info("Logout requested. Clearing access and refresh tokens.")
    return response


@router.get("/sign-in")
def sign_in_handler():
    logger.info("Sign-in page requested")
    refresh_token = request.cookies.get("refresh")
    payload = validate_token(refresh_token)

    if payload:
        logger.info(f"Valid refresh token found for user_id={payload.get('user_id')}, auto-signing in.")
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
    logger.info("No valid refresh token, rendering sign-in page.")
    return render_template("signin.html", google_link=google_auth_url)


@router.get("/sign-up")
def sign_up_handler():
    logger.info("Sign-up page requested")
    access = request.cookies.get("access")
    refresh = request.cookies.get("refresh")
    if access or refresh:
        logger.info("Session ended")
        return redirect("/auth/logout")
    return render_template("signup.html", google_link=google_auth_url)


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


    user = User(
        first_name=first_name,
        last_name=last_name,
        phone_number=phone_number,
        email=email,
        password=hashed_password
    )
    try:
        session.add(user)
        session.commit()
        verifier.send_confirmation_email(email, user.id)
        logger.info(f"Successfully created user account for: {email}")
        return redirect("/auth/sign-in")
    except IntegrityError:
        session.rollback()
        logger.warning(f"Sign-up failed: user with email {email} already exists.")
        return "error, user exists"
    except SQLAlchemyError as e:
        session.rollback()
        logger.exception(f"Unexpected DB error during sign-up for {email}: {e}")
        return "Internal Server Error"


@router.post("/sign-in/submit")
def sign_in_sub_handler():
    email = request.form.get("email")
    password = request.form.get("password")

    logger.info(f"Received sign-up submission for: {email}")

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


@router.get("/verify")
def verification_handler():
    code = request.args.get("code")
    user_id = verifier.verify(code)
    if user_id:
        try:
            user = session.query(User).get(user_id)
            user.is_verified = True
            session.add(user)
            session.commit()
            logger.info(f"User: {user_id}, successfully verified their account.")
            return redirect("/account")
        except Exception as e:
            logger.error(f"User: {user_id} could not verify their account")
    logger.error("Error occurred")
    return render_template("error.html")

