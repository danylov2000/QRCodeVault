from flask import Blueprint, render_template, request
import logging
import segno.helpers

import segno
import urllib.parse
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


@qrcode_router.get("/textgen")
def qrcode_sms_handler():
    logger.info("User entered sms qr-gen")
    return render_template("qr_sms_message.html")


@qrcode_router.get("/email")
def qrcode_email_handler():
    logger.info("User entered email qr-gen")
    return render_template("qr_email_gen.html")


@qrcode_router.get("/phonecall")
def qrcode_phone_handler():
    logger.info("User entered phone-call qr-gen")
    return render_template("qr_phone_call_gen.html")


@qrcode_router.get("/wifi")
def qrcode_wifi_handler():
    logger.info("User entered wifi qr-gen")
    return render_template("qr_wifi_gen.html")


@qrcode_router.get("/event")
def qrcode_event_handler():
    logger.info("User entered calendar-event qr-gen")
    return render_template("qr_event_gen.html")


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

    elif qr_type == "text":

        message_text = request.form.get("message")

        phone_number = request.form.get("phone")

        encoded_message = urllib.parse.quote(message_text)

        message_uri = f"sms:{phone_number}?body={encoded_message}"

        qrcode = segno.make(message_uri)

        qr = QrCode(qr_type=qr_type, pickle_obj=qrcode, user=user)

        session.add(qr)
        session.commit()

        return render_template("qrcode_display.html", qr_image_url=qrcode.svg_data_uri())
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

        qr = QrCode(qr_type=qr_type, pickle_obj=qrcode, user=user)

        session.add(qr)
        session.commit()

        return render_template("qrcode_display.html", qr_image_url=qrcode.svg_data_uri())

    elif qr_type == "email":
        email = request.form.get("to_email")
        cc_emails = request.form.get("cc_email")
        bcc_email = request.form.get("bcc_email")
        subject = request.form.get("subject")
        body = request.form.get("body")

        qrcode = segno.helpers.make_email(to=email, cc=cc_emails, bcc=bcc_email, subject=subject, body=body)

        qr = QrCode(qr_type=qr_type, pickle_obj=qrcode, user=user)

        session.add(qr)
        session.commit()

        return render_template("qrcode_display.html", qr_image_url=qrcode.svg_data_uri())

    elif qr_type == "call":
        phone = request.form.get("phone")
        qrcode = segno.make(f"tel:{phone}")
        qr = QrCode(qr_type=qr_type, pickle_obj=qrcode, user=user)

        session.add(qr)
        session.commit()

        return render_template("qrcode_display.html", qr_image_url=qrcode.svg_data_uri())

    elif qr_type == "wifi":
        wifi_name = request.form.get("ssid")
        wifi_pass = request.form.get("password")
        wifi_encryption = request.form.get("encryption")

        qrcode = segno.helpers.make_wifi(ssid=wifi_name, password=wifi_pass, security=wifi_encryption)
        qr = QrCode(qr_type=qr_type, pickle_obj=qrcode, user=user)

        session.add(qr)
        session.commit()

        return render_template("qrcode_display.html", qr_image_url=qrcode.svg_data_uri())


    # elif qr_type == "calendar":
    #
    #     from datetime import datetime
    #
    #     import textwrap
    #
    #     event_title = request.form.get("summary")
    #
    #     description = request.form.get("description")
    #
    #     location = request.form.get("location")
    #
    #     start = request.form.get("start")  # format: YYYY-MM-DD HH:MM
    #
    #     end = request.form.get("end")
    #
    #     start_time = datetime.strptime(start, "%Y-%m-%dT%H:%M").strftime("%Y%m%dT%H%M%SZ")
    #     end_time = datetime.strptime(end, "%Y-%m-%dT%H:%M").strftime("%Y%m%dT%H%M%SZ")
    #
    #     calendar_event = textwrap.dedent(f"""\
    #         BEGIN:VCALENDAR
    #         VERSION:2.0
    #         BEGIN:VEVENT
    #         SUMMARY:{event_title}
    #         DESCRIPTION:{description}
    #         LOCATION:{location}
    #         DTSTART:{start_time}
    #         DTEND:{end_time}
    #         END:VEVENT
    #         END:VCALENDAR
    #     """)
    #
    #     qrcode = segno.make(calendar_event)
    #
    #     qr = QrCode(qr_type=qr_type, pickle_obj=qrcode, user=user)
    #
    #     session.add(qr)
    #
    #     session.commit()
    #
    #     return render_template("qrcode_display.html", qr_image_url=qrcode.svg_data_uri())
