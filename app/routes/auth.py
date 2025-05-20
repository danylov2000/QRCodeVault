from flask import Blueprint, render_template, request
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

    user = User(first_name, last_name, phone_number, email, password)
    session.add(user)
    session.commit()
    return "Ok"



