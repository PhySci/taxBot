import datetime
import logging
import os
import unittest

from sqlalchemy import Column, String, Integer, ForeignKey, create_engine, DateTime
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

from settings import DATABASE_URL

Base = declarative_base()

_logger = logging.getLogger(__name__)

STATUS_OK = 0
STATUS_RECEIPT_UNKNOWN_USER = 1
STATUS_RECEIPT_ALREADY_EXIST = 2
STATUS_USER_ALREADY_EXIST = 3

STATUS_FAIL = 10

class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    tg_id = Column(Integer)
    first_name = Column(String)
    last_name = Column(String)
    patronymic_name = Column(String)
    email = Column(String)
    status = Column(String)
    role = Column(String)
    registration_dt = Column(DateTime(timezone=True), server_default=func.now())
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
        self._db_url = os.environ.get("DATABASE_URL")
        self._engine = create_engine(self._db_url)
        self._sm = sessionmaker(bind=self._engine)
        Base.metadata.create_all(self._engine)

    def reinit(self):
        session = self._sm()
        try:
            session.query(User).delete()
            session.query(Receipt).delete()
        except Exception as err:
            print(repr(err))

        try:
            Base.metadata.create_all(self._engine)
        except Exception as err:
            print(repr(err))

    def __del__(self):
        pass
        #self._session.close()

    def add_user(self, user: dict):
        session = self._sm()

        c = session.query(User.id).filter(User.tg_id == user["tg_id"]).count()
        if c > 0:
            return STATUS_USER_ALREADY_EXIST

        new_user = User(
            tg_id=int(user['tg_id']),
            first_name=user['first_name'],
            last_name=user['last_name'],
            patronymic_name=user['patronymic_name'],
            email=user['email'],
            status="active",
            role="user"
        )

        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        id = new_user.id
        session.close()

        if id is not None:
            return STATUS_OK
        else:
            return STATUS_FAIL


    def add_receipt(self, receipt: dict):
        """

        :param receipt: {"user_id": int, "text": str}
        :return:
        """
        session = self._sm()
        user_id = session.query(User.id).filter(User.tg_id == receipt["tg_id"]).first()
        if user_id is None:
            return STATUS_RECEIPT_UNKNOWN_USER
        receipt = Receipt(**receipt)
        receipt.user_id = user_id[0]
        receipt.status = "active"
        session.add(receipt)
        session.commit()

        session.refresh(receipt)
        id = receipt.id
        session.close()

        if id is not None:
            return STATUS_OK
        else:
            return STATUS_FAIL

    def get_receipts(self):
        pass
