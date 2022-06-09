import datetime
import os
import unittest
from unittest import TestCase
from dotenv import load_dotenv
from src.db import DBDriver, STATUS_OK, STATUS_RECEIPT_UNKNOWN_USER, \
    STATUS_USER_ALREADY_EXIST, STATUS_RECEIPT_ALREADY_EXIST, STATUS_USER_ALREADY_DEACTIVATED, STATUS_FAIL
import random


conf_pth = os.path.join(os.path.dirname(__file__), '.env')
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
        user_id = random.randint(10, int(1e7))
        user = {"tg_id": user_id,
                    "first_name": "Иван",
                    "last_name": "Иванов",
                    "patronymic_name": "Петрович",
                    "email": "test@ya.ru"}
        self.assertEqual(d.add_user(user), STATUS_OK)
        self.assertEqual(d.add_user(user), STATUS_USER_ALREADY_EXIST)

    def test_deactivate_user(self):
        d = DBDriver()
        user_id = random.randint(10, 1e7)
        user = {"tg_id": user_id,
                    "first_name": "Сергей",
                    "last_name": "Александрович",
                    "patronymic_name": "Родищев",
                    "email": "test@ya.ru"}
        self.assertEqual(d.deactivate_user(user), STATUS_FAIL)

        d.add_user(user)
        self.assertEqual(d.deactivate_user(user), STATUS_OK)
        self.assertEqual(d.deactivate_user(user), STATUS_USER_ALREADY_DEACTIVATED)

    def test_add_receipt(self):
        d = DBDriver()

        text = "https://lknpd.nalog.ru/api/v1/receipt/" + str(random.randint(0, int(1e7))) + "/ab123d/print"
        new_receipt = {"tg_id": 1,
                       "text": text}
        self.assertEqual(d.add_receipt(new_receipt), STATUS_OK)
        self.assertEqual(d.add_receipt(new_receipt), STATUS_RECEIPT_ALREADY_EXIST)


    def test_add_receipt_unknown_user(self):
        d = DBDriver()
        text = "https://lknpd.nalog.ru/api/v1/receipt/" + str(random.randint(0, int(1e7))) + "/123abcdfsdf/print"
        receipt = {"tg_id": 2,
                   "text": text}
        status = d.add_receipt(receipt)
        self.assertEqual(status, STATUS_RECEIPT_UNKNOWN_USER)

    def test_get_receipts(self):
        d = DBDriver()
        start_date = datetime.datetime.now()
        end_date = datetime.datetime.now() + datetime.timedelta(minutes=2)
        result = {
            'data':
                [{
                    'tg_id': 1,
                    'text': f'https://example.link/api/v1/receipt/{random.randint(0, int(1e7))}/print',
                    'create_dt': datetime.datetime.now() + datetime.timedelta(minutes=1),
                    'update_dt': None
                }]
        }
        d.add_receipt(result['data'][0])
        x = d.get_receipts(start_date=start_date, end_date=end_date)
        self.assertEqual(x['data'][0]['create_dt'], result['data'][0]['create_dt'].strftime("%d-%m-%Y"))
        self.assertEqual(x['data'][0]['text'], result['data'][0]['text'])


    def test_get_period(self):
        driver = DBDriver()
        r = driver.get_period()


if __name__ == "__main__":
    unittest.main()
