import datetime
import logging
import os
from datetime import datetime
import smtplib


from email import encoders
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import xlsxwriter

from settings import EMAIL_LOGIN, EMAIL_PASSWORD, SMTP_SERVER, SMTP_PORT
from db import STATUS_OK, STATUS_FAIL, DBDriver, SendingStatus
from utils import setup_logging

_logger = logging.getLogger(__name__)


def json_to_excel(json_data: dict) -> str:
    """
    Formats the input data and saves as Excel file

    :param json_data:
    :return:
    """
    file_pth = os.path.join(os.path.dirname(__file__), "tmp", datetime.now().strftime("%Y-%m-%d_%H-%M-%S")+".xlsx")
    workbook = xlsxwriter.Workbook(file_pth)
    worksheet = workbook.add_worksheet()

    clear_data = []

    for el in json_data["data"]:
        clear_data.append({"FIO": " ".join([el.get("last_name", ""),
                                            el.get("first_name", ""),
                                            el.get("patronymic_name", "")]),
                           "Email": el.get("email"),
                           "Date": el.get("create_dt", ""),
                           "Receipt": el.get("text", "")})

    headers = ["ФИО", "e-mail", "Дата получения", "Чек"]

    for col, h in enumerate(headers):
        worksheet.write(0, col, h)

    for row, el in enumerate(clear_data):
        worksheet.write(row+1, 0, el["FIO"])
        worksheet.write(row+1, 1, el["Email"])
        worksheet.write(row+1, 2, el["Date"])
        worksheet.write(row+1, 3, el["Receipt"])

    workbook.close()
    return file_pth


def send_email(email_list: list, excel_filepath: str) -> SendingStatus:
    msg = MIMEMultipart()
    msg['Subject'] = "Mailing list from the TaxBot according to your request (EXCEL file)"
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
        server = smtplib.SMTP_SSL(host=SMTP_SERVER, port=SMTP_PORT, timeout=5)
        server.login(EMAIL_LOGIN, EMAIL_PASSWORD)
        server.sendmail(EMAIL_LOGIN, msg['To'], msg.as_string())
        server.quit()
        _logger.info("E-mail has been sent successfully. STATUS_OK")
        return SendingStatus.OK
    except smtplib.SMTPException as e:
        _logger.error("E-mail has not been sent: %s", repr(e))
        return SendingStatus.FAILED


def main():
    driver = DBDriver()
    email_list = driver.get_email_list_for_sending()

    if len(email_list) == 0:
        _logger.error("E-mail list is empty. Check records in database")
        return STATUS_FAIL

    period_start_date, period_end_date = driver.get_period()

    receipts = driver.get_receipts(period_start_date, period_end_date)
    excel_filepath = json_to_excel(receipts)
    status = send_email(email_list, excel_filepath)

    driver.save_period(datetime.today(), period_start_date, period_end_date, len(receipts["data"]), status)


def execute_mailing_in_chat():
    driver = DBDriver()
    json_data = driver.get_receipts()
    excel_filepath = json_to_excel(json_data)
    return excel_filepath


if __name__ == "__main__":
    #@TODO: argparse input arguments if they are
    setup_logging()
    main()