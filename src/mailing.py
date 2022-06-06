import logging
import os
import smtplib

from email import encoders
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from json2excel import Json2Excel

from settings import EMAIL_LOGIN, EMAIL_PASSWORD
from src.db import STATUS_OK, STATUS_FAIL, DBDriver

_logger = logging.getLogger(__name__)


def json_to_excel(json_data):
    clear_data = json_data["data"]
    json_loader = Json2Excel(head_name_cols=["create_dt", "update_dt"])
    return json_loader.run(clear_data)


def execute_mailing():
    driver = DBDriver()
    email_list = driver.get_email_list_for_sending()
    if email_list is None:
        _logger.error("E-mail list is empty. Check records in database")
        raise TypeError(
            "Variable 'email_list' has type None, but must be of type 'list'. "
            "This error possibly related with database"
        )
    else:
        json_data = driver.get_receipts()
        excel_filepath = json_to_excel(json_data)
        msg = MIMEMultipart()
        msg['Subject'] = "Mailing list from the taxBot according to your request (EXCEL file)"
        msg['From'] = EMAIL_LOGIN
        msg['To'] = ', '.join(email_list)
        body = "This is an automated email"
        msg.attach(MIMEText(body, 'plain'))
        part = MIMEBase('application', "octet-stream")
        with open(excel_filepath, "rb") as file:
            part.set_payload(file.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename="{os.path.basename(excel_filepath)}"')
        msg.attach(part)
        os.remove(excel_filepath)
        try:
            server = smtplib.SMTP_SSL(host="smtp.yandex.ru", port=465, timeout=5)
            server.login(EMAIL_LOGIN, EMAIL_PASSWORD)
            server.sendmail(EMAIL_LOGIN, msg['To'], msg.as_string())
            server.quit()
            _logger.info("E-mail has been sent successfully. STATUS_OK")
            return STATUS_OK
        except smtplib.SMTPException as e:
            _logger.error("E-mail has not been sent: %s", repr(e))
            return STATUS_FAIL
