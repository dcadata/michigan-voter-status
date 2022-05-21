from email.mime.text import MIMEText
from os import environ
from smtplib import SMTP_SSL


def send_email(subject: str, body: str):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = environ['SENDER']
    msg['To'] = environ['RECIPIENT']

    server = SMTP_SSL(host='smtp.gmail.com', port=465)
    server.login(environ['SENDER'], environ['PASSWORD'])
    server.send_message(msg)
    server.quit()
