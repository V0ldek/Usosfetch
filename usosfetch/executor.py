import requests
import os
from usosfetch.authorizer import Authorizer
from usosfetch.data_manager import DataManager
from usosfetch.notifier import Notifier

EMAIL = 'matgienieczko@gmail.com'


def main():

    with requests.Session() as session:

        authorizer = Authorizer(session)
        data_manager = DataManager(session)
        notifier = Notifier(EMAIL)

        try:
            authorizer.login(os.environ["USOS_USERNAME"], os.environ["USOS_PASSWORD"])

            old_grades = data_manager.get_old_grades()
            new_grades = data_manager.get_new_grades()

            data_diff = data_manager.get_differences(old_grades, new_grades)

            if data_diff:
                notifier.notify(data_diff)
                print('New grades!')
            else:
                print('Nihil novi.')

            data_manager.save_grades(new_grades)

        finally:
            authorizer.logout()
