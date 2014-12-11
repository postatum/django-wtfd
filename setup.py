#!/usr/bin/env python
# -*- coding: utf-8 -*-
try:
    from setuptools import setup
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup


setup(
    name='django_wtfd',
    version='0.1.4',
    description='Forcing developers to write docstrings.',
    author='Artem Kostiuk',
    author_email='postatum@gmail.com',
    long_description=open('README.md', 'r').read(),
    url='https://github.com/postatum/django-wtfd',
    download_url = 'https://github.com/postatum/django-wtfd/tarball/0.1.4',
    packages=[
        'django_wtfd',
        'django_wtfd.management',
        'django_wtfd.management.commands',
    ],
    install_requires=['bettor_admin'],
    dependency_links=[
        'git+https://github.com/Bettor/bettor_admin@master#egg=bettor_admin',
    ],
    keywords = ['docs', 'docstrings'],
    classifiers = [],
    zip_safe=False,
)
