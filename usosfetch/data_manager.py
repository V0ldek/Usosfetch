from lxml import html
import json
import configparser
import psycopg2
import os


class DataManager:

    _session = None
    _urls = None
    _logger = None

    def __init__(self, session, logger):
        self._session = session
        self._logger = logger

        config = configparser.ConfigParser()
        config.read('usosfetch/config.ini')
        self._urls = config.items('GRADES')

    def _get_grade_tree(self, url):
        grade_get_result = self._session.get(url)

        if not grade_get_result.ok:
            raise RuntimeError('Failed to fetch grade data for ' + url + ' with code ' +
                               str(grade_get_result.status_code))

        self._logger.log('Fetched grades from ' + str(url) + '.')

        return html.fromstring(grade_get_result.content)

    def _get_grade_trees(self):
        trees = []

        for (name, url) in self._urls:
            trees.append((name, self._get_grade_tree(url)))

        return trees

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
