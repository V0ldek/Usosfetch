from lxml import html

LOGIN_POST = 'https://logowanie.uw.edu.pl/cas/login'
LOGIN_GET = 'https://usosweb.mimuw.edu.pl/kontroler.php?_action=logowaniecas/index'
LOGOUT_GET = 'https://usosweb.mimuw.edu.pl/kontroler.php?_action=logowaniecas/wyloguj'


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

        login_get_result = self._session.get(LOGIN_GET).result()

        get_result_tree = html.fromstring(login_get_result.content)

        if Authorizer._is_success(get_result_tree):
            return

        ticket = get_result_tree.xpath('//input[@name="lt"]/@value')

        self._login_payload['lt'] = ticket[0]

        login_post_result = self._session.post(LOGIN_POST, data=self._login_payload).result()

        post_result_tree = html.fromstring(login_post_result.content)

        if not Authorizer._is_success(post_result_tree):
            raise RuntimeError("Login attempt failed.")

    def logout(self):
        self._session.get(LOGOUT_GET).result()
