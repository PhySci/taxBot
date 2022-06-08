import logging
import os

from sqlalchemy import Column, String, Integer, ForeignKey, create_engine, DateTime, Boolean
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

_logger = logging.getLogger(__name__)

Base = declarative_base()

STATUS_OK = 0
STATUS_RECEIPT_UNKNOWN_USER = 1
STATUS_RECEIPT_ALREADY_EXIST = 2
STATUS_USER_ALREADY_EXIST = 3
STATUS_USER_ALREADY_DEACTIVATED = 4
STATUS_MAIL_ALREADY_EXIST = 5
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
    use_reminder = Column(Boolean)
    create_dt = Column(DateTime(timezone=True), server_default=func.now())
    update_dt = Column(DateTime(timezone=True), onupdate=func.now())
    receipts = relationship("Receipt")


class Receipt(Base):
    __tablename__ = 'receipt'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    status = Column(String)
    text = Column(String)
    tg_id = Column(String)
    create_dt = Column(DateTime(timezone=True), server_default=func.now())
    update_dt = Column(DateTime(timezone=True), onupdate=func.now())


class MailList(Base):
    __tablename__ = 'maillist'
    id = Column(Integer, primary_key=True)
    status = Column(String)
    email = Column(String)
    create_dt = Column(DateTime(timezone=True), server_default=func.now())


class DBDriver:

    def __init__(self):
        _DB_NAME = os.environ.get("DB_NAME")
        _DB_ADDRESS = os.environ.get("DB_ADDRESS")
        _DB_PORT = os.environ.get("DB_PORT")
        _DB_USER = os.environ.get("DB_USER")
        _DB_PASSWORD = os.environ.get("DB_PASSWORD")
        self._database_url = f"postgresql://{_DB_USER}:{_DB_PASSWORD}@" \
                             f"{_DB_ADDRESS}:{_DB_PORT}/{_DB_NAME}"
        self._engine = create_engine(self._database_url)
        self._sm = sessionmaker(bind=self._engine)
        Base.metadata.create_all(self._engine)

    def reinit(self):
        session = self._sm()
        try:
            session.query(Receipt).delete()
            session.query(User).delete()
            session.commit()
        except Exception as err:
            print(repr(err))

        try:
            Base.metadata.create_all(self._engine)
        except Exception as err:
            print(repr(err))

    def __del__(self):
        pass
        # self._session.close()

    def add_user(self, user: dict):
        session = self._sm()

        c = session.query(User.id).filter(User.tg_id == user["tg_id"]).count()
        if c > 0:
            _logger.warning(
                f"User '{user['first_name']} {user['patronymic_name']} {user['last_name']}' with "
                f"telegram id '{user['tg_id']}' already exists in database. STATUS_USER_ALREADY_EXIST"
            )
            return STATUS_USER_ALREADY_EXIST

        new_user = User(
            tg_id=int(user['tg_id']),
            first_name=user['first_name'],
            last_name=user['last_name'],
            patronymic_name=user['patronymic_name'],
            email=user['email'],
            status="active",
            role="user",
            use_reminder=False
        )

        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        id = new_user.id
        session.close()

        if id is not None:
            _logger.info(
                f"User '{user['first_name']} {user['patronymic_name']} {user['last_name']}' "
                f"with telegram id '{user['tg_id']}' has been added successfully. STATUS_OK"
            )
            return STATUS_OK
        else:
            _logger.error(
                f"User '{user['first_name']} {user['patronymic_name']} {user['last_name']}' "
                f"with telegram id '{user['tg_id']}' has not been added. STATUS_FAIL"
            )
            return STATUS_FAIL

    def deactivate_user(self, user: dict):
        session = self._sm()
        db_user = session.query(User).filter(User.tg_id == user["tg_id"])
        if db_user.count() == 0:
            _logger.error(
                f"User '{user['first_name']} {user['patronymic_name']} {user['last_name']}' with "
                f"telegram id '{user['tg_id']}' does not exists in database. STATUS_FAIL"
            )
            return STATUS_FAIL

        user = db_user.one()

        if user.status == "deactive":
            _logger.warning(
                f"Status of user with id '{user.id}' is already 'deactive'. "
                f"STATUS_USER_ALREADY_DEACTIVATED"
            )
            return STATUS_USER_ALREADY_DEACTIVATED

        user.status = "deactive"
        session.commit()
        status = user.status
        session.close()
        if status == "deactive":
            _logger.info(f"Status of user with id '{user.id}' has been changed to 'deactive'. STATUS_OK")
            return STATUS_OK


    def is_user_exist(self, user_id: int):
        session = self._sm()
        if session.query(User).filter(User.tg_id == user_id).count():
            return True
        else:
            return False

    def add_receipt(self, receipt: dict):
        """

        :param receipt: {"user_id": int, "text": str}
        :return:
        """
        session = self._sm()
        user_id = session.query(User.id).filter(User.tg_id == receipt["tg_id"]).first()
        if user_id is None:
            _logger.warning(f"User with id '{user_id}' is not found. STATUS_RECEIPT_UNKNOWN_USER")
            return STATUS_RECEIPT_UNKNOWN_USER
        user_id = user_id[0]
        if session.query(Receipt.id).filter(Receipt.text == receipt["text"]).count() > 0:
            _logger.warning(
                f"Receipt with text '{receipt['text']}' already "
                f"exists in database. STATUS_RECEIPT_ALREADY_EXIST"
            )
            return STATUS_RECEIPT_ALREADY_EXIST
        receipt = Receipt(**receipt)
        receipt.user_id = user_id
        receipt.status = "active"
        session.add(receipt)
        session.commit()
        session.refresh(receipt)
        id = receipt.id
        session.close()
        if id is not None:
            _logger.warning(f"Receipt with id '{id}' has been added successfully. STATUS_OK")
            return STATUS_OK
        else:
            _logger.error(f"Receipt with text {receipt['text']} has not been added. STATUS_FAIL")
            return STATUS_FAIL

    def get_receipts(self) -> dict:
        """
        Returns JSON with all receipts

        :return:
        """
        session = self._sm()
        res = {"data": []}
        data = session.query(
            User.first_name,
            User.patronymic_name,
            User.last_name,
            Receipt.text,
            Receipt.create_dt,
            Receipt.update_dt).filter(User.id == Receipt.user_id).all()
        for element in data:
            element = element._asdict()
            try:
                element["create_dt"] = element["create_dt"].strftime("%d-%m-%Y")
            except AttributeError as error:
                element["create_dt"] = None
                _logger.exception(error)
            try:
                element["update_dt"] = element["update_dt"].strftime("%d-%m-%Y")
            except AttributeError:
                element["update_dt"] = None
            res["data"].append(element)
        return res

    def add_email_for_sending(self, email: str):
        session = self._sm()
        c = session.query(MailList.id).filter(MailList.email == email).count()
        if c > 0:
            _logger.warning(f"E-mail {email} already exists in database. STATUS_MAIL_ALREADY_EXIST")
            return STATUS_MAIL_ALREADY_EXIST
        new_email = MailList(
            email=email,
            status="active",
        )
        session.add(new_email)
        session.commit()
        session.refresh(new_email)
        id = new_email.id
        session.close()
        if id is not None:
            _logger.info(f"E-mail {email} has been added successfully. STATUS_OK")
            return STATUS_OK
        else:
            _logger.error(f"E-mail {email} has not been added. STATUS_FAIL")
            return STATUS_FAIL

    def get_email_list_for_sending(self):
        session = self._sm()
        data = session.query(MailList.email).all()
        if data:
            return [''.join(x) for x in data]
        else:
            return None
