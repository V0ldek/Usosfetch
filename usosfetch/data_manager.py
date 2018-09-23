from lxml import html
import json
import psycopg2
import os
import re

GRADES_PREFIX = 'GRADES_'


class GradesManager:

    _session = None
    _urls = None
    _logger = None

    def __init__(self, session, logger):
        self._session = session
        self._logger = logger

        self._urls = self._get_grades_config()

    @staticmethod
    def _get_grades_config():
        return {(k[len(GRADES_PREFIX):].lower(), v) for (k, v) in os.environ.items()
                if re.match('^' + GRADES_PREFIX + '.*', k) is not None}

    def _get_grade_tree_request(self, name, url):
        self._logger.log('Fetching grades for ' + name + ' from ' + str(url) + '...')

        return self._session.get(url)

    def _get_grade_tree_from_request(self, name, request):

        if not request.ok:
            raise RuntimeError('Failed to fetch grade data for ' + name + 'with code ' +
                               str(request.status_code))

        self._logger.log('Fetched grades for ' + name + '.')

        return html.fromstring(request.content)

    def _get_grade_trees(self):
        requests = {(n, self._get_grade_tree_request(n, u)) for (n, u) in self._urls}

        return {(n, self._get_grade_tree_from_request(n, r.result())) for (n, r) in requests}

    @staticmethod
    def _parse_grade_tree(tree):

        tables = tree.xpath('//table[@class="grey"]')

        grades = list(map(lambda t: t.xpath('descendant::td/b/text()'), tables))

        return grades

    def _load_grades(self):

        with psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require') as db, db.cursor() as cursor:

            for (name, _) in self._urls:
                cursor.execute("""SELECT count(*) FROM grades WHERE id = %s""", (name,))
                result = cursor.fetchone()

                if result == (0,):
                    self._logger.log('Grade ' + name + ' entry not found in the database, inserting a new row.')
                    cursor.execute("""INSERT INTO grades VALUES (%s, %s)""", (name, '[]'))

            cursor.execute("""SELECT * FROM grades""")
            result = cursor.fetchall()

        return list(map(lambda n_s: (n_s[0], json.loads(n_s[1])), result))

    @staticmethod
    def _save_grades(set_name, grades, cursor):

        new_grades = json.dumps(grades)

        cursor.execute("""UPDATE grades SET List = %s WHERE ID = %s""", (new_grades, set_name))

    def get_new_grades(self):
        return sorted(list(map(lambda n_t: (n_t[0], self._parse_grade_tree(n_t[1])), self._get_grade_trees())))

    def get_old_grades(self):
        names = list(map(lambda n_u: n_u[0], self._urls))

        return sorted(list(filter(lambda n_l: n_l[0] in names, self._load_grades())))

    def save_grades(self, grades_list):

        db = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')

        cursor = db.cursor()

        for (name, grades) in grades_list:
            self._save_grades(name, grades, cursor)

        db.commit()

        cursor.close()
        db.close()

    @staticmethod
    def get_differences(old_grades, new_grades):
        differences = []

        if len(old_grades) != len(new_grades):
            raise RuntimeError('List length mismatch in DataManager.get_differences: '
                               + str(len(old_grades)) + ' != ' + str(len(new_grades)))

        for ((old_name, old_grade), (_, new_grade)) in zip(old_grades, new_grades):
            if old_grade != new_grade:
                differences.append(old_name)

        return differences
