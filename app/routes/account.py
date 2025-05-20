from flask import Blueprint

router = Blueprint("account", __name__)

@router.get("/")
def account_page_handler():
    return "account page"