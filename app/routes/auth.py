from flask import Blueprint, render_template, request, jsonify, redirect
from sqlalchemy.exc import IntegrityError
from app.utils import hash_pass, create_access_tokens
from app.database.models import User
from app.database import session

router = Blueprint("auth", __name__)


@router.get("/sign-in")
def sign_in_handler():
    return render_template("signin.html")


@router.get("/sign-up")
def sign_up_handler():
    return render_template("signup.html")


@router.post("/sign-up/submit")
def sign_up_sub_handler():
    data = request.form
    first_name = data.get("firstName")
    last_name = data.get("lastName")
    phone_number = data.get("phone")
    email = data.get("email")
    password = data.get("password")

    hashed_password = hash_pass(password)

    user = User(first_name, last_name, phone_number, email, hashed_password)
    try:
        session.add(user)
        session.commit()
        return redirect("/auth/sign-in")
    except IntegrityError:
        session.rollback()
        return "error, user exists"

@router.post("/sign-in/submit")
def sign_in_sub_handler():
    email = request.form.get("email")
    password = request.form.get("password")

    hashed_password = hash_pass(password)

    user = session.query(User).where(User.email == email).where(User.password == hashed_password).one_or_none()

    if not user:
        return redirect("/auth/sign-up")
    else:


        return f"Hello, {user.first_name}"









