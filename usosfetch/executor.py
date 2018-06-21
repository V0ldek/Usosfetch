import requests
import os
from usosfetch.authorizer import Authorizer
from usosfetch.data_manager import DataManager
from usosfetch.notifier import Notifier


def main():

    with requests.Session() as session:

        authorizer = Authorizer(session)
        data_manager = DataManager(session)
        notifier = Notifier(os.environ['RECEIVER_EMAIL'])

        try:
            authorizer.login(os.environ["USOS_USERNAME"], os.environ["USOS_PASSWORD"])

            print('Login successful.')

            old_grades = data_manager.get_old_grades()

            print('Loaded old grades: ' + str(old_grades))

            new_grades = data_manager.get_new_grades()

            print('Fetched new grades: ' + str(new_grades))

            data_diff = data_manager.get_differences(old_grades, new_grades)

            print('Differences: ' + str(data_diff))

            if data_diff:
                notifier.notify(data_diff)
                print('New grades!')
            else:
                print('Nihil novi.')

            data_manager.save_grades(new_grades)

            print('Updated the database.')

        finally:
            authorizer.logout()
