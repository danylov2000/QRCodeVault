from flask import Blueprint, render_template

router = Blueprint("main", __name__)

@router.get("/")
def main_page_handler():
    return render_template("home.html")
