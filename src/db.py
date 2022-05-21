from datetime import datetime
import logging

from sqlalchemy import Column, DateTime, String, Integer, ForeignKey, func, create_engine, distinct
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import MetaData

from typing import Dict, List

Base = declarative_base()

_logger = logging.getLogger(__name__)


class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    tg_name = Column(String)
    email = Column(String)
    registration_dt = Column(String)
    recepts = relationship("Recept")


class Recept(Base):
    __tablename__ = 'recept'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    status = Column(String)
    url = Column(String)


class DBDriver:

    def __init__(self):
        self._db_url = "DATABASE_URL"
        self._engine = create_engine(self._db_url)
        sm = sessionmaker()
        sm.configure(bind=self._engine)
        self._session = sm()

    def add_user(self, user: dict):
        pass

    def add_recept(self, recept: dict):
        pass

    def get_recepts(self):
        pass

