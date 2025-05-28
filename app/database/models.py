from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, Integer, String, Table, ForeignKey
from sqlalchemy.types import PickleType

Base = declarative_base()

class User(Base):

    __tablename__ = "users"

    id = Column(Integer, autoincrement=True, nullable=False, primary_key=True)
    first_name = Column(String, nullable=False, unique=False)
    last_name = Column(String, nullable=False, unique=False)
    phone_number = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, unique=False, nullable=False)

    qrcodes = relationship("QrCode", back_populates="user")

    def __init__(self, first_name, last_name, phone_number, email, password):
        self.first_name = first_name
        self.last_name = last_name
        self.phone_number = phone_number
        self.email = email
        self.password = password

class QrCode(Base):

    __tablename__ = "qrcodes"

    id = Column(Integer, autoincrement=True, nullable=False, primary_key=True)
    qr_type = Column(String, nullable=False, unique=False)
    pickle_obj = Column(PickleType, nullable=False, unique=False)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False, unique=False)
    user = relationship("User", back_populates="qrcodes")

    def get_svg(self):
        return self.pickle_obj.svg_data_uri()



