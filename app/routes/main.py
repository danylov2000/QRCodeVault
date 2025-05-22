from flask import Blueprint, render_template
import logging

router = Blueprint("main", __name__)

logger = logging.getLogger(__name__)

@router.get("/")
def main_page_handler():
    logger.info("User requested home page")
    return render_template("home.html")
