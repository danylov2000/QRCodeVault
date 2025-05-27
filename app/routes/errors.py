
from flask import render_template
import logging

logger = logging.getLogger(__name__)


def not_found(error):
    logger.error("That URL is not found")
    return render_template("error.html"), 404

