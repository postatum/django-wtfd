import os
import ast

from django.core.management.base import BaseCommand
from django.conf import settings

from ... import MissingDocstringsException


class Command(BaseCommand):
    """
    Parses Django project's modules and checks whether all of them
    have docstrings.
    """
    EXCLUDES = (
        'meta',
    )

    def __init__(self, *args, **kwargs):
        """
        Get WTFD_APPS setting from Django settings on init.
        """
        self.apps = getattr(settings, 'WTFD_APPS', [])
        self.strict_mode = getattr(settings, 'WTFD_STRICT', False)
        self.reports = []
        super(Command, self).__init__(*args, **kwargs)

    def _validate_filename(self, filename):
        """
        Checks filename to only fetch .py files & don't fetch tests.
        """
        is_pyfile = filename.endswith('.py')
        not_test = 'test' not in filename
        return (filename and is_pyfile and not_test)

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
            try:
                module = __import__(app.split('.')[-1])
            except ImportError:
                print 'Skipping not valid app: {}'.format(app)
                continue
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

    def _valid_node(self, node):
        """
        Checks if a node is either class or func and if it
        should be excluded from checks.
        """
        if not isinstance(node, (ast.ClassDef, ast.FunctionDef)):
            return False
        magic_method = node.name.startswith('__')
        in_excluded = node.name.lower() in self.EXCLUDES
        if magic_method or in_excluded:
            return False
        return True

    def _store_report(self, node, file_path):
        """
        Reports missing docstrings on a node.
        """
        schema = '\033[94m{}\033[0m \033[95m{}\033[0m line {}'
        report = schema.format(node.name, file_path, unicode(node.lineno))
        self.reports.append(report)

    def check_docstrings(self, file_path):
        """
        Parses the file located on :file_path: and
        prints a report if any class or method is missing
        docstringsin in it.
        """
        with open(file_path) as f:
            f_content = f.read()
        syntax_tree = ast.parse(f_content)

        for node in ast.walk(syntax_tree):
            if not self._valid_node(node):
                continue
            doc = ast.get_docstring(node)
            doc = None if doc is None else doc.strip()
            if not doc:
                self._store_report(node, file_path)

    def report_missing_docstrings(self):
        """
        Prints or raises report on missing docstrings.
        WTFD_STRICT == True  => Raises
        WTFD_STRICT == False => Prints
        """
        if not any(self.reports):
            return
        traceback = '\n'.join(self.reports)
        if self.strict_mode:
            raise MissingDocstringsException(traceback)
        print '\033[91mMissing docstrings:\033[0m'
        print traceback

    def handle(self, *args, **options):
        """
        High-level logic. Calls other methods.
        """
        files = self.collect_filenames()
        for file_path in files:
            self.check_docstrings(file_path)

        self.report_missing_docstrings()
