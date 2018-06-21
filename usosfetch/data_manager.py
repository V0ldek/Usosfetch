from lxml import html
import json
import configparser
from utils.print import open_html


class DataManager:

    _session = None
    _urls = None

    def __init__(self, session):
        self._session = session

        config = configparser.ConfigParser()
        config.read('usosfetch/config.ini')
        self._urls = config.items('GRADES')

    def _get_grade_tree(self, url):
        grade_get_result = self._session.get(url)

        if not grade_get_result.ok:
            raise RuntimeError('Failed to fetch grade data for ' + url + ' with code ' + str(grade_get_result.response))

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

    @staticmethod
    def _load_grades(name):
        file = open('usosfetch/grades/' + name + '.json', 'r')

        result = json.load(file)

        file.close()

        return result

    @staticmethod
    def _save_grades(name, grades):
        file = open('usosfetch/grades/' + name + '.json', 'w')

        file.write(json.dumps(grades))

        file.close()

    def get_new_grades(self):
        return list(map(lambda n_t: (n_t[0], self._parse_grade_tree(n_t[1])), self._get_grade_trees()))

    def get_old_grades(self):
        return list(map(lambda n_u: (n_u[0], self._load_grades(n_u[0])), self._urls))

    def save_grades(self, grades_list):
        for (name, grades) in grades_list:
            self._save_grades(name, grades)

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
