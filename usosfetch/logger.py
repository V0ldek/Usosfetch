from datetime import datetime
import json
import psycopg2
import os

LOG = 'Log'
ERROR = 'ERROR'


class Logger:

    _log = {}

    def _log_entry(self, severity, date, message):
        print(severity + ': ' + str(date) + ': ' + str(message))
        self._log[str(date)] = severity + ': ' + str(message)

    def begin_session(self):
        self._log_entry(LOG, datetime.now(), 'Begin log session.')

    def log(self, message):
        self._log_entry(LOG, datetime.now(), message)

    def error(self, message):
        self._log_entry(ERROR, datetime.now(), message)

    def save_to_database(self):

        with psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require') as db, db.cursor() as cursor:

            row = json.dumps(self._log, sort_keys=True, indent=4, separators=(',', ': '))

            cursor.execute("""INSERT INTO logs (log) VALUES (%s)""", (row,))
