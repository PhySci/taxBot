import unittest
from mailing import execute_mailing

class TestMail(unittest.TestCase):

    def test_send_email(self):
        execute_mailing()

if __name__ == "__main__":
    unittest.main()


