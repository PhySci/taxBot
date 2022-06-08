import unittest
from dotenv import load_dotenv
import os

conf_pth = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(conf_pth, )

from mailing import execute_mailing, json_to_excel
from db import DBDriver


class TestMail(unittest.TestCase):

    def test_send_email(self):
        execute_mailing()


class TestExcel(unittest.TestCase):

    def test_excel(self):
        driver = DBDriver()
        receipts = driver.get_receipts()
        pth = json_to_excel(receipts)
        print(pth)


if __name__ == "__main__":
    unittest.main()


