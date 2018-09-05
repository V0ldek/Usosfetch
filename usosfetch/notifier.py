import smtplib
import os
from email.mime.text import MIMEText


class Notifier:

    _email = None

    def __init__(self, email):
        self._email = email

    def _compose_email(self, data):

        msg = MIMEText('You have new grades in: ' + str(data) + '!\n')

        msg['Subject'] = 'New grades in ' + str(data) + '!'
        msg['From'] = os.environ['NOTIFIER_USERNAME']
        msg['To'] = self._email

        return msg

    def notify(self, data):

        msg = self._compose_email(data)

        smtp = smtplib.SMTP(os.environ['SMTP_HOST'], os.environ['SMTP_PORT'])
        smtp.starttls()
        smtp.login(os.environ['NOTIFIER_USERNAME'], os.environ['NOTIFIER_PASSWORD'])
        smtp.sendmail(os.environ['NOTIFIER_USERNAME'], [self._email], msg.as_string())
