import os
import unittest
from unittest import TestCase
from dotenv import load_dotenv
from db import DBDriver, STATUS_OK, STATUS_RECEIPT_UNKNOWN_USER, STATUS_USER_ALREADY_EXIST, STATUS_RECEIPT_ALREADY_EXIST
import random

conf_pth = os.path.join(os.path.dirname(__file__), 'env')
load_dotenv(dotenv_path=conf_pth)


class TestDB(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        d = DBDriver()
        #d.reinit()

        user = {"tg_id": 1,
                "first_name": "Иван",
                "last_name": "Иванов",
                "patronymic_name": "Петрович",
                "email": "test@ya.ru"}
        d.add_user(user)


    def test_init(self):
        try:
            DBDriver()
        except Exception as err:
            self.fail(repr(err))

    def test_add_user(self):
        d = DBDriver()
        user_id = random.randint(10, 1e7)
        user = {"tg_id": user_id,
                    "first_name": "Иван",
                    "last_name": "Иванов",
                    "patronymic_name": "Петрович",
                    "email": "test@ya.ru"}
        self.assertEqual(d.add_user(user), STATUS_OK)
        self.assertEqual(d.add_user(user), STATUS_USER_ALREADY_EXIST)

    def test_add_receipt(self):
        d = DBDriver()

        text = "https://lknpd.nalog.ru/api/v1/receipt/" + str(random.randint(0, 1e7)) + "/ab123d/print"
        new_receipt = {"tg_id": 1,
                       "text": text}
        self.assertEqual(d.add_receipt(new_receipt), STATUS_OK)
        self.assertEqual(d.add_receipt(new_receipt), STATUS_RECEIPT_ALREADY_EXIST)

    def test_add_receipt_unknown_user(self):
        d = DBDriver()
        text = "https://lknpd.nalog.ru/api/v1/receipt/" + str(random.randint(0, 1e7)) + "/123abcdfsdf/print"
        receipt = {"tg_id": 2,
                   "text": text}
        status = d.add_receipt(receipt)
        self.assertEqual(status, STATUS_RECEIPT_UNKNOWN_USER)


if __name__ == "__main__":
    unittest.main()
