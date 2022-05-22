from datetime import datetime
import logging

from sqlalchemy import Column, DateTime, String, Integer, ForeignKey, func, create_engine, distinct
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import MetaData

from typing import Dict, List
from settings import DATABASE_URL

Base = declarative_base()

_logger = logging.getLogger(__name__)


class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    tg_id = Column(Integer)
    email = Column(String)
    registration_dt = Column(String)
    recepts = relationship("Recept")


class Recept(Base):
    __tablename__ = 'recept'
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
        pass

    def add_recept(self, recept: dict):
        pass

    def get_recepts(self):
        pass

