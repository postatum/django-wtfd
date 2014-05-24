from __future__ import absolute_import

import os

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def filename_checker(self, x):
        return (
            x and
            x.endswith('.py') and
            not x.startswith('__') and
            ('test' not in x)
        )

    def collect_filenames(self):
        collected = []
        for root, dirnames, filenames in os.walk('.'):
            if root.endswith('/migrations'):
                continue
            filenames = filter(self.filename_checker, filenames)
            collected += [os.path.join(root, f) for f in filenames]
        return collected

    def handle(self, *args, **options):
        filenames = self.collect_filenames()
        print filenames
