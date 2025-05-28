from flask import Blueprint, render_template
import logging

router = Blueprint("main", __name__)

logger = logging.getLogger(__name__)

@router.get("/")
def main_page_handler():
    logger.info("User requested home page")
    return render_template("home.html")

@router.get("/blog")
def blog_page_handler():
    logger.info("User entered blog page")
    return render_template("blog.html")

@router.get("/support")
def support_page_handler():
    logger.info("User entered support page")
    return render_template("support.html")

