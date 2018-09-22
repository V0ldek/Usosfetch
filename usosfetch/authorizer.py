from lxml import html
import os


class Authorizer:

    _login_payload = {
        '_eventId': 'submit',
        'execution': 'e1s1',
        'lt': '',
        'password': '',
        'submit': 'ZALOGUJ',
        'username': ''
    }

    _session = None

    _urls = None

    def __init__(self, session):
        self._session = session

    @staticmethod
    def _is_success(tree):
        return not bool(tree.xpath('//body[@id="cas"]'))

    def login(self, username, password):
        self._login_payload['username'] = username
        self._login_payload['password'] = password

        login_get_result = self._session.get(os.environ['LOGIN_GET'])

        get_result_tree = html.fromstring(login_get_result.content)

        if Authorizer._is_success(get_result_tree):
            return

        ticket = get_result_tree.xpath('//input[@name="lt"]/@value')

        self._login_payload['lt'] = ticket[0]

        login_post_result = self._session.post(os.environ['LOGIN_POST'], data=self._login_payload)

        post_result_tree = html.fromstring(login_post_result.content)

        if not Authorizer._is_success(post_result_tree):
            raise RuntimeError("Login attempt failed.")

    def logout(self):
        self._session.get(os.environ['LOGOUT_GET'])
