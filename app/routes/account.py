from flask import Blueprint, render_template
from app.middlewares import auth_required

router = Blueprint("account", __name__)

@router.get("/")
@auth_required
def account_page_handler(payload):
    return render_template("account.html", name=payload["full_name"])



