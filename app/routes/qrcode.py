from flask import Blueprint, render_template, request
import logging
import segno.helpers
import segno

from app.middlewares import auth_required
from app.database import session
from app.database.models import User, QrCode

qrcode_router = Blueprint("qrcode", __name__)
logger = logging.getLogger(__name__)


@qrcode_router.get("/")
def qrcode_options_handler():
    logger.info("User entered selector for qr-code")
    return render_template("qrcodeselection.html")


@qrcode_router.get("/urlgen")
def qrcode_websitegen_handler():
    logger.info("User entered website url qr-generator")
    return render_template("qrwebsiteurl.html")


@qrcode_router.get("/mapgen")
def qrcode_map_handler():
    logger.info("User entered location/map qr-generator")
    return render_template("qrmaplocation.html")


@qrcode_router.get("/vcard")
def qrcode_vcard_handler():
    logger.info("User entered vcard qr-gen")
    return render_template("qrvcard.html")


@qrcode_router.post("/generate")
@auth_required
def qrcode_generate_handler(payload):
    qr_type = request.args.get("type")

    user = session.query(User).get(payload["user_id"])

    if qr_type == "url":

        qrcode = segno.make(request.form.get("url"), micro=False)

        qr = QrCode(qr_type=qr_type, pickle_obj=qrcode, user=user)
        session.add(qr)
        session.commit()

        return render_template("qrcode_display.html", qr_image_url=qrcode.svg_data_uri())
    elif qr_type == "map":
        lat = float(request.form.get("latitude"))
        long = float(request.form.get("longitude"))
        qrcode = segno.helpers.make_geo(lat, long)

        qr = QrCode(qr_type=qr_type, pickle_obj=qrcode, user=user)
        session.add(qr)
        session.commit()

        return render_template("qrcode_display.html", qr_image_url=qrcode.svg_data_uri())
