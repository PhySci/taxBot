import os
import smtplib

from email import encoders
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from json2excel import Json2Excel

from settings import EMAIL_LOGIN, EMAIL_PASSWORD
from src.db import STATUS_OK, STATUS_FAIL


def json_to_excel(json):
    clear_data = json["data"]
    json_loader = Json2Excel(head_name_cols=["create_dt", "update_dt"])
    return json_loader.run(clear_data)


def send_email(destination, filepath):
    msg = MIMEMultipart()
    msg['Subject'] = "Mailing list from the taxBot according to your request (XLS file)"
    msg['From'] = EMAIL_LOGIN
    msg['To'] = ', '.join(destination)

    body = "This is an automated email"
    msg.attach(MIMEText(body, 'plain'))

    part = MIMEBase('application', "octet-stream")
    with open(filepath, "rb") as file:
        part.set_payload(file.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f'attachment; filename="{os.path.basename(filepath)}"')
    msg.attach(part)
    try:
        smtpObj = smtplib.SMTP('smtp.gmail.com', 587)
        smtpObj.starttls()
        smtpObj.login(EMAIL_LOGIN, EMAIL_PASSWORD)
        smtpObj.sendmail(EMAIL_LOGIN, destination, msg.as_string())
        smtpObj.quit()
        return STATUS_OK
    except smtplib.SMTPException:
        return STATUS_FAIL
