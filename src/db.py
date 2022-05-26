import datetime
import logging

from sqlalchemy import Column, String, Integer, ForeignKey, create_engine, DateTime
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from settings import DATABASE_URL

Base = declarative_base()

_logger = logging.getLogger(__name__)


class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    tg_id = Column(Integer)
    first_name = Column(String)
    last_name = Column(String)
    patronymic_name = Column(String)
    email = Column(String)
    registration_dt = Column(
        DateTime,
        server_default=datetime.datetime.utcnow)
    receipts = relationship("Receipt")


class Receipt(Base):
    __tablename__ = 'receipt'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    status = Column(String)
    text = Column(String)
    tg_id = Column(String)


class DBDriver:

    def __init__(self):
        self._db_url = DATABASE_URL
        self._engine = create_engine(self._db_url)
        self._session = sessionmaker().configure(bind=self._engine)

    def __del__(self):
        self._session.close()

    def add_user(self, user: dict):
        new_user = User(
            tg_id=int(user['tg_id']),
            first_name=user['first_name'],
            last_name=user['last_name'],
            patronymic_name=user['patronymic_name'],
            email=user['email'],
        )
        self._session.add(new_user)
        self._session.commit()

    def add_receipt(self, receipt: dict):
        pass

    def get_receipts(self):
        pass
