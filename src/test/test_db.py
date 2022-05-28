import os
import unittest
from unittest import TestCase
from dotenv import load_dotenv
from db import DBDriver, STATUS_OK, STATUS_RECEIPT_UNKNOWN_USER, STATUS_USER_ALREADY_EXIST, STATUS_RECEIPT_ALREADY_EXIST

conf_pth = os.path.join(os.path.dirname(__file__), 'env')
r = load_dotenv(dotenv_path=conf_pth)
import random

class TestDB(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        d = DBDriver()
        #d.reinit()

    def test_init(self):
        try:
            DBDriver()
        except Exception as err:
            self.fail(repr(err))

    def test_add_user(self):
        d = DBDriver()
        new_user = {"tg_id": random.randint(0, 1e7),
                    "first_name": "Иван",
                    "last_name": "Иванов",
                    "patronymic_name": "Петрович",
                    "email": "test@ya.ru"}
        self.assertEqual(d.add_user(new_user), STATUS_OK)

    def test_add_receipt(self):
        d = DBDriver()
        new_receipt = {"tg_id": 1,
                       "text": "https://lknpd.nalog.ru/api/v1/receipt/0000000000/123abcdfsdf/print"}
        status = d.add_receipt(new_receipt)
        self.assertEqual(status, STATUS_OK)

    def test_add_receipt_unknown_user(self):
        d = DBDriver()
        text = "https://lknpd.nalog.ru/api/v1/receipt/" + str(random.randint(0, 1e7)) +  "/123abcdfsdf/print"
        receipt = {"tg_id": 1111,
                       "text": text }
        status = d.add_receipt(receipt)
        self.assertEqual(status, STATUS_RECEIPT_UNKNOWN_USER)

        status = d.add_receipt(receipt)



if __name__ == "__main__":
    unittest.main()
