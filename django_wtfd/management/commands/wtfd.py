import os
import ast

from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    """
    Parses Django project's modules and checks whether all of them
    have docstrings.
    """

    def __init__(self, *args, **kwargs):
        """
        Get WTFD_APPS setting from Django settings on init.
        """
        self.apps = getattr(settings, 'WTFD_APPS', [])
        self.reports = []
        super(Command, self).__init__(*args, **kwargs)

    def _validate_filename(self, filename):
        """
        Checks filename to only fetch .py files & don't fetch tests.
        """
        is_pyfile = filename.endswith('.py')
        not_magic = not filename.startswith('__')
        not_test = 'test' not in filename
        return (filename and is_pyfile and not_magic and not_test)

    def _valid_path(self, path):
        """
        Check path so it won't contain migrations/tests directories.
        """
        not_migrations = not path.endswith('/migrations')
        not_tests = not path.endswith('/tests')
        return (not_migrations and not_tests)

    def collect_filenames(self):
        """
        Collects filenames from self.apps or all the project.
        """
        if not self.apps:
            return self._collect_mod_filenames()
        collected = []
        for app in self.apps:
            module = __import__(app.split('.')[-1])
            collected += self._collect_mod_filenames(module.__path__[0])
        return collected

    def _collect_mod_filenames(self, path='.'):
        """
        Collect filenames on given path.
        """
        collected = []
        for root, dirnames, filenames in os.walk(path):
            if not self._valid_path(root):
                continue
            filenames = filter(self._validate_filename, filenames)
            collected += [os.path.join(root, f) for f in filenames]
        return collected

    def check_docstrings(self, file_path):
        """
        Parses the file located on :file_path: and
        prints a report if any class or method is missing
        docstringsin in it.
        """
        with open(file_path) as f:
            f_content = f.read()
        syntax_tree = ast.parse(f_content)

        schema = 'Missing docstrings: {} ({}, line {})'

        for node in ast.walk(syntax_tree):
            if not isinstance(node, (ast.ClassDef, ast.FunctionDef)):
                continue
            doc = ast.get_docstring(node)
            doc = None if doc is None else doc.strip()
            if doc:
                continue
            report = schema.format(node.name, file_path, unicode(node.lineno))
            print report
            self.reports.append(report)

    def handle(self, *args, **options):
        """
        High-level logic. Calls other methods.
        """
        files = self.collect_filenames()
        for file_path in files:
            self.check_docstrings(file_path)
