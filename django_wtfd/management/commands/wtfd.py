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

    def handle(self, *args, **options):
        """
        High-level logic. Calls other methods.
        """
        filenames = self.collect_filenames()
        print filenames
