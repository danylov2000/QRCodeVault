import os

from flask import Flask
from .routes import main, auth, account

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
template_dir = os.path.join(BASE_DIR, 'templates')


application = Flask(__name__, template_folder=template_dir)
application.secret_key = os.getenv("SECRET_KEY")


application.register_blueprint(main.router)
application.register_blueprint(auth.router, url_prefix="/auth")
application.register_blueprint(account.router, url_prefix="/account")


