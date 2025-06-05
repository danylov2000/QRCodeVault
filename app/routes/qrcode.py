from datetime import datetime, timezone

from flask import Blueprint, render_template, request
import logging
import segno.helpers
import segno
import urllib.parse

from werkzeug.utils import redirect

from app.middlewares import auth_required
from app.database import session
from app.database.models import User, QrCode

qrcode_router = Blueprint("qrcode", __name__)
logger = logging.getLogger(__name__)


@qrcode_router.get("/")
@auth_required
def qrcode_options_handler(payload):
    logger.info("User entered selector for qr-code")
    return render_template("qrcodeselection.html")


@qrcode_router.get("/urlgen")
@auth_required
def qrcode_websitegen_handler(payload):
    logger.info("User entered website url qr-generator")
    return render_template("qrwebsiteurl.html")


@qrcode_router.get("/mapgen")
@auth_required
def qrcode_map_handler(payload):
    logger.info("User entered location/map qr-generator")
    return render_template("qrmaplocation.html")


@qrcode_router.get("/vcard")
@auth_required
def qrcode_vcard_handler(payload):
    logger.info("User entered vcard qr-gen")
    return render_template("qrvcard.html")


@qrcode_router.get("/textgen")
@auth_required
def qrcode_sms_handler(payload):
    logger.info("User entered sms qr-gen")
    return render_template("qr_sms_message.html")


@qrcode_router.get("/email")
@auth_required
def qrcode_email_handler(payload):
    logger.info("User entered email qr-gen")
    return render_template("qr_email_gen.html")


@qrcode_router.get("/phonecall")
@auth_required
def qrcode_phone_handler(payload):
    logger.info("User entered phone-call qr-gen")
    return render_template("qr_phone_call_gen.html")


@qrcode_router.get("/wifi")
@auth_required
def qrcode_wifi_handler(payload):
    logger.info("User entered wifi qr-gen")
    return render_template("qr_wifi_gen.html")


@qrcode_router.get("/event")
@auth_required
def qrcode_event_handler(payload):
    logger.info("User entered calendar-event qr-gen")
    return render_template("qr_event_gen.html")


@qrcode_router.post("/generate")
@auth_required
def qrcode_generate_handler(payload):
    timestamp = datetime.now(timezone.utc).isoformat()

    qr_type = request.args.get("type")

    user = session.query(User).get(payload["user_id"])

    if not user:
        logger.warning(f"[{timestamp}] QR code generation failed: user_id={payload['user_id']} not found.")
        return render_template("error.html")

    logger.info(f"[{timestamp}] QR code generation started by user_id={user.id}, name={user.get_full_name()}, type={qr_type}")
    try:
        if qr_type == "url":

            qrcode = segno.make(request.form.get("url"), micro=False)


        elif qr_type == "map":
            lat = float(request.form.get("latitude"))
            long = float(request.form.get("longitude"))
            qrcode = segno.helpers.make_geo(lat, long)


        elif qr_type == "text":

            message_text = request.form.get("message")
            phone_number = request.form.get("phone")
            encoded_message = urllib.parse.quote(message_text)
            message_uri = f"sms:{phone_number}?body={encoded_message}"

            qrcode = segno.make(message_uri)


        elif qr_type == "vcard":
            first_name = request.form.get("first_name")
            last_name = request.form.get("last_name")
            m_phone = request.form.get("mobile")
            p_phone = request.form.get("phone1")
            fax = request.form.get("fax")
            email = request.form.get("email")
            company = request.form.get("company")
            title = request.form.get("job_title")
            street = request.form.get("street")
            city = request.form.get("city")
            c_zip = request.form.get("zip")
            state = request.form.get("state")
            country = request.form.get("country")
            website = request.form.get("website")

            qrcode = segno.helpers.make_vcard(
                name=f"{first_name} {last_name}",
                displayname=f"{first_name} {last_name}",
                cellphone=m_phone,
                homephone=p_phone,
                fax=fax,
                email=email,
                org=company,
                title=title,
                street=street,
                city=city,
                zipcode=c_zip,
                region=state,
                country=country,
                url=website)

        elif qr_type == "email":
            email = request.form.get("to_email")
            cc_emails = request.form.get("cc_email")
            bcc_email = request.form.get("bcc_email")
            subject = request.form.get("subject")
            body = request.form.get("body")

            qrcode = segno.helpers.make_email(to=email, cc=cc_emails, bcc=bcc_email, subject=subject, body=body)

        elif qr_type == "call":
            phone = request.form.get("phone")
            qrcode = segno.make(f"tel:{phone}")


        elif qr_type == "wifi":
            wifi_name = request.form.get("ssid")
            wifi_pass = request.form.get("password")
            wifi_encryption = request.form.get("encryption")

            qrcode = segno.helpers.make_wifi(ssid=wifi_name, password=wifi_pass, security=wifi_encryption)

        else:
            return render_template("error.html")

        qr = QrCode(qr_type=qr_type, pickle_obj=qrcode, user=user)
        session.add(qr)
        session.commit()



        return redirect(f"/qrcode/view/{qr.id}")
    except Exception as e:
        logger.error(f"[{timestamp}] Error generating QR code for user_id={user.id}, type={qr_type}: {str(e)}")
        return render_template("error.html")


@qrcode_router.get("/view/<qr_id>")
@auth_required
def qr_view_handler(payload, qr_id):
    qrcode = session.query(QrCode).get(qr_id)

    if qrcode is None:
        logger.error(f"Qrcode with id:{qr_id} doesnt exist")
        return render_template("error.html")
    elif qrcode.user_id != payload["user_id"]:
        logger.error("Qrcode does not exist for this user")
        return render_template("error.html")

    return render_template("qrcode_display.html", qr_image_url=qrcode.get_svg(), qr_id=qr_id)

@qrcode_router.get("/remove/<qr_id>")
@auth_required
def qr_remove_handler(payload, qr_id):

    qrcode = session.query(QrCode).get(qr_id)
    if qrcode is None:
        logger.error("qrcode not found")
        return render_template("error.html")
    elif qrcode.user_id != payload["user_id"]:
        logger.error("Qrcode does not exist for this user")
        return render_template("error.html")
    session.delete(qrcode)
    session.commit()
    return redirect("/account")



