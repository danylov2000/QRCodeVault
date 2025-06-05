from flask import Blueprint, render_template
from app.middlewares import auth_required
from app.database import session
from app.database.models import User
import logging
from datetime import datetime, timezone
from flask import request

logger = logging.getLogger(__name__)
router = Blueprint("account", __name__)

@router.get("/")
@auth_required
def account_page_handler(payload):
    user_id = payload["user_id"]
    full_name = payload["full_name"]

    user = session.query(User).get(user_id)

    if not user:
        logger.warning(
            f"[{datetime.now(timezone.utc).isoformat()}] Failed to load account page: "
            f"user_id={user_id} not found."
        )
        return "User not found", 404

    qr_code_count = len(user.qrcodes) if user.qrcodes else 0
    ip = request.remote_addr

    logger.info(
        f"[{datetime.now(timezone.utc).isoformat()}] Account page accessed | "
        f"user_id={user_id} | name='{full_name}' | QR codes={qr_code_count} | IP={ip}"
    )

    return render_template("account.html", name=full_name, qr_codes=user.qrcodes)

# @router.get("/qrcode")
# def qrcode_options_handler():
#     return render_template("qrcodeselection.html")





