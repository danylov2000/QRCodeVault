from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Table

Base = declarative_base()

class User(Base):

    __tablename__ = "users"

    id = Column(Integer, autoincrement=True, nullable=False, primary_key=True)
    first_name = Column(String, nullable=False, unique=False)
    last_name = Column(String, nullable=False, unique=False)
    phone_number = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, unique=False, nullable=False)

    def __init__(self, first_name, last_name, phone_number, email, password):
        self.first_name = first_name
        self.last_name = last_name
        self.phone_number = phone_number
        self.email = email
        self.password = password
