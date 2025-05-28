from flask import Blueprint, render_template
from app.middlewares import auth_required
from app.database import session
from app.database.models import User

router = Blueprint("account", __name__)

@router.get("/")
@auth_required
def account_page_handler(payload):
    user = session.query(User).get(payload["user_id"])


    return render_template("account.html", name=payload["full_name"], qr_codes=user.qrcodes)

# @router.get("/qrcode")
# def qrcode_options_handler():
#     return render_template("qrcodeselection.html")





