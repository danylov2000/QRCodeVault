from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from os import environ
from .models import Base

db_user = environ.get("DB_USER")
db_pass = environ.get("DB_PASSWORD")
db_host = environ.get("DB_HOST")
db_name = environ.get("DB_NAME")
db_port = environ.get("DB_PORT")

engine = create_engine(f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}")

Base.metadata.create_all(bind=engine)

session = Session(bind=engine)

