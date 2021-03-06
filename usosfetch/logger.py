from datetime import datetime
import json
import psycopg2
import os

LOG = 'Log'
ERROR = 'ERROR'


class Logger:

    _log = {}
    _is_error = False

    def __init__(self):
        self.log('Begin log session.')

    def _log_entry(self, severity, date, message):
        print(severity + ': ' + str(date) + ': ' + str(message))
        self._log[str(date)] = severity + ': ' + str(message)

    def log(self, message):
        self._log_entry(LOG, datetime.now(), message)

    def error(self, message):
        self._is_error = True
        self._log_entry(ERROR, datetime.now(), message)

    def save_to_database(self):

        with psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require') as db, db.cursor() as cursor:

            row = json.dumps(self._log, sort_keys=True, indent=4, separators=(',', ': '))

            cursor.execute("""INSERT INTO logs (log, is_error, timestamp) VALUES (%s, %s, %s)""",
                           (row, self._is_error, datetime.now()))

    def clear_old_logs(self):

        with psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require') as db, db.cursor() as cursor:

            cursor.execute("""DELETE FROM logs WHERE timestamp < now() - INTERVAL %s""",
                           ("'" + os.environ['LOG_EXPIRATION_DAYS'] + " days'",))

            self.log('Deleted ' + str(cursor.rowcount) + ' old logs.')
