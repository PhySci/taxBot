import datetime
import logging
import os

from sqlalchemy import Column, String, Integer, ForeignKey, create_engine, DateTime
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func


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
        #Base.metadata.create_all(self._engine)

    def __del__(self):
        pass
        #self._session.close()

    def add_user(self, user: dict):
        new_user = User(
            tg_id=int(user['tg_id']),
            first_name=user['first_name'],
            last_name=user['last_name'],
            patronymic_name=user['patronymic_name'],
            email=user['email'],
        )
        session = self._sm()
        session.add(new_user)
        session.commit()
        session.close()

    def add_receipt(self, receipt: dict):
        pass

    def get_receipts(self):
        pass
