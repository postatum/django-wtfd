django_wtfd
===========

wtfd(write the f*ing docs) is a Django library that forces developers to write docstrings.

Developed on Django 1.5.8


Installation
------------

1. pip install django_wtfd

2. Add django_wtfd to your project's INSTALLED_APPS.


Settings
--------

WTFD_APPS
    List of project's apps to include in docstrings check. If its not set all the .py files in project will be checked.

WTFD_STRICT
    If set to True, checks will raise an exception in case some method/function/class is missing docstrings. Defaults to False.


Usage
-----

To perform docstrings check, run: ./manage.py wtfd


Notes
-----

- Docstrings check skips magic methods, migrations, Meta class and modules that have 'test' in their name.
