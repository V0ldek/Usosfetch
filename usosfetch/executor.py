import requests_futures.sessions
import os
import traceback
from usosfetch.authorizer import Authorizer
from usosfetch.data_manager import GradesManager
from usosfetch.notifier import Notifier
from usosfetch.logger import Logger


def main():
    logger = Logger()
    authorizer = None

    with requests_futures.sessions.FuturesSession() as session:

        try:
            notifier = Notifier(os.environ['RECEIVER_EMAIL'], logger)

            authorizer = Authorizer(session)
            data_manager = GradesManager(session, logger)

            authorizer.login(os.environ["USOS_USERNAME"], os.environ["USOS_PASSWORD"])

            logger.log('Login successful.')

            old_grades = data_manager.get_old_grades()

            logger.log('Loaded old grades: ' + str(old_grades))

            new_grades = data_manager.get_new_grades()

            logger.log('Fetched new grades: ' + str(new_grades))

            data_diff = data_manager.get_differences(old_grades, new_grades)

            if not data_diff:
                logger.log('Nihil novi.')
                return 0

            logger.log('New grades in' + str(data_diff) + '!')

            notifier.notify(data_diff)

            logger.log('Notification sent.')

            data_manager.save_grades(new_grades)

            logger.log('Updated the database.')

        except Exception:
            logger.error(traceback.format_exc())
            raise
        finally:
            if authorizer is not None:
                authorizer.logout()
            if logger is not None:
                logger.clear_old_logs()
                logger.save_to_database()
