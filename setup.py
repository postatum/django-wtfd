#!/usr/bin/env python
# -*- coding: utf-8 -*-
from distutils.core import setup


setup(
    name='django_wtfd',
    version='0.1',
    description='Forcing developers to write docstrings.',
    author='Artem Kostiuk',
    author_email='postatum@gmail.com',
    long_description=open('README.rst', 'r').read(),
    url='https://github.com/postatum/django-wtfd',
    download_url = 'https://github.com/postatum/django-wtfd/tarball/0.1',
    packages=[
        'django_wtfd',
        'django_wtfd.management',
        'django_wtfd.management.commands',
    ],
    keywords = ['docs', 'docstrings'],
    classifiers = [],
    zip_safe=False,
)
