import smtplib
from email.mime.text import MIMEText

USERNAME = 'usosfetch.py.smtp@gmail.com'
PASSWORD = 'aGHP7r3aL7WCNFzz'


class Notifier:

    _email = None

    def __init__(self, email):
        self._email = email

    def _compose_email(self, data):

        msg = MIMEText('You have new grades in: ' + str(data) + '!\n')

        msg['Subject'] = 'New grades in ' + str(data) + '!'
        msg['From'] = USERNAME
        msg['To'] = self._email

        return msg

    def notify(self, data):

        msg = self._compose_email(data)

        smtp = smtplib.SMTP('smtp.gmail.com', 587)
        smtp.starttls()
        smtp.login(USERNAME, PASSWORD)
        smtp.sendmail(USERNAME, [self._email], msg.as_string())
