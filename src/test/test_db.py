import os
import unittest
from unittest import TestCase
from dotenv import load_dotenv
from db import DBDriver

conf_pth = os.path.join(os.path.dirname(__file__), 'env')
r = load_dotenv(dotenv_path=conf_pth)


class TestDB(TestCase):

    def test_init(self):
        try:
            DBDriver()
        except Exception as err:
            self.fail(repr(err))

    def test_add_user(self):
        d = DBDriver()
        new_user = {"tg_id": 1456,
                    "first_name": "Иван",
                    "last_name": "Иванов",
                    "patronymic_name": "Петрович",
                    "email": "test@ya.ru"}
        d.add_user(new_user)



if __name__ == "__main__":
    unittest.main()
