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
        smtpObj = smtplib.SMTP('smtp.gmail.com', 587)
        smtpObj.starttls()
        smtpObj.login(EMAIL_LOGIN, EMAIL_PASSWORD)
        smtpObj.sendmail(EMAIL_LOGIN, msg['To'], msg.as_string())
        smtpObj.quit()
        _logger.error("E-mail has been sent successfully. STATUS_FAIL")
        return STATUS_OK
    except smtplib.SMTPException:
        _logger.error("E-mail has not been sent. STATUS_FAIL")
        return STATUS_FAIL
