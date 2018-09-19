import smtplib
import os
from email.mime.text import MIMEText


class Notifier:

    _email = None
    _logger = None

    def __init__(self, email, logger):
        self._email = email
        self._logger = logger

    def _compose_email(self, data):

        msg = MIMEText('You have new grades in: ' + str(data) + '!\n')

        msg['Subject'] = 'New grades in ' + str(data) + '!'
        msg['From'] = os.environ['NOTIFIER_USERNAME']
        msg['To'] = self._email

        return msg

    def notify(self, data):

        msg = self._compose_email(data)

        self._logger.log('Sending an email to ' + self._email + ' via ' +
                         os.environ['SMTP_HOST'] + ':' + os.environ['SMTP_PORT'])

        smtp = smtplib.SMTP(os.environ['SMTP_HOST'], os.environ['SMTP_PORT'])
        smtp.starttls()
        smtp.login(os.environ['NOTIFIER_USERNAME'], os.environ['NOTIFIER_PASSWORD'])
        smtp.sendmail(os.environ['NOTIFIER_USERNAME'], [self._email], msg.as_string())
