from django.test import TestCase
from django.test.utils import override_settings

from mock import patch, Mock

from .management.commands.wtfd import Command
from . import MissingDocstringsException


TEST_APP_NAME = 'test_app'


class WTFDCommandTestCase(TestCase):
    """
    Tests for wtfd command.
    """

    def setUp(self):
        self.cmd = Command()

    @override_settings(WTFD_APPS=[TEST_APP_NAME])
    @override_settings(WTFD_STRICT=True)
    def test_init(self):
        cmd = Command()
        # Attributes exist
        self.assertTrue(hasattr(cmd, 'reports'))
        self.assertTrue(hasattr(cmd, 'apps'))
        self.assertTrue(hasattr(cmd, 'strict_mode'))
        # Attributes are valid
        self.assertEqual(cmd.reports, [])
        self.assertEqual(cmd.apps, [TEST_APP_NAME])
        self.assertTrue(cmd.strict_mode)

    def test_validate_filename(self):
        # Python file
        self.assertTrue(self.cmd._validate_filename('file.py'))
        # Not python
        self.assertFalse(self.cmd._validate_filename('file.jpg'))
        # Tests
        self.assertFalse(self.cmd._validate_filename('test.py'))
        self.assertFalse(self.cmd._validate_filename('models_tests.py'))
        self.assertFalse(self.cmd._validate_filename('test_views.py'))

    def test_valid_path(self):
        # Excludes migrations and tests
        self.assertFalse(self.cmd._valid_path('app/migrations'))
        self.assertFalse(self.cmd._valid_path('app/tests'))
        # Valid path
        self.assertTrue(self.cmd._valid_path('app/imports'))

    @patch('django_wtfd.management.commands.wtfd.Command._collect_mod_filenames')
    def test_collect_filenames_no_apps(self, mock_meth):
        self.cmd.apps = []
        self.cmd.collect_filenames()
        mock_meth.assert_called_once_with()

    @patch('django_wtfd.management.commands.wtfd.Command._collect_mod_filenames')
    def test_collect_filenames(self, mock_meth):
        self.cmd.apps = ['django', 'django_wtfd']
        self.cmd.collect_filenames()
        self.assertTrue(len(mock_meth.mock_calls) >= 2)

    @patch('django_wtfd.management.commands.wtfd.Command._collect_mod_filenames')
    def test_collect_filenames_invalid_app(self, mock_meth):
        self.cmd.apps = ['1d81h2d8h192dh2397dh2973h3d_____']
        self.cmd.collect_filenames()
        self.assertFalse(mock_meth.called)

    def test_collect_mod_filenames_syntax(self):
        collected = self.cmd._collect_mod_filenames()
        self.assertTrue(any(collected))

    def test_valid_node_invalid_class(self):
        name = 'noone_can_guess_this_name_srs'
        node = Mock(name=name)
        self.assertFalse(self.cmd._valid_node(node))

    def test_valid_node_valid_class(self):
        from ast import ClassDef, FunctionDef
        name = 'noone_can_guess_this_name_srs'
        self.assertTrue(self.cmd._valid_node(ClassDef(name=name)))
        self.assertTrue(self.cmd._valid_node(FunctionDef(name=name)))

    def test_valid_node_corner_cases(self):
        from ast import ClassDef, FunctionDef
        name = 'noone_can_guess_this_name_srs'
        self.assertTrue(self.cmd._valid_node(ClassDef(name=name)))
        self.assertTrue(self.cmd._valid_node(FunctionDef(name=name)))

    def test_store_report(self):
        node = Mock(name='Node', lineno=42)
        self.assertEqual(self.cmd.reports, [])
        self.cmd._store_report(node, '/tmp/')
        self.assertEqual(len(self.cmd.reports), 1)

    def test_check_docstrings_syntax(self):
        # TODO: Write more sane test.
        filename = self.cmd._collect_mod_filenames()[0]
        self.cmd.check_docstrings(filename)

    def test_report_missing_docstrings_no_reports(self):
        self.cmd.strict_mode = True
        self.cmd.reports = []
        try:
            self.cmd.report_missing_docstrings()
        except MissingDocstringsException:
            self.fail("report_missing_docstrings() raised "
                      "MissingDocstringsException unexpectedly!")

    def test_report_missing_docstrings_reports(self):
        self.cmd.strict_mode = True
        self.cmd.reports = ['asd']
        self.assertRaises(
            MissingDocstringsException,
            self.cmd.report_missing_docstrings,
        )

    @patch('django_wtfd.management.commands.wtfd.Command.collect_filenames')
    @patch('django_wtfd.management.commands.wtfd.Command.check_docstrings')
    @patch('django_wtfd.management.commands.wtfd.Command.report_missing_docstrings')
    def test_handle(self, mock_report, mock_check, mock_collect):
        mock_collect.return_value = ['asd']
        self.cmd.handle()
        mock_collect.assert_called_once_with()
        mock_check.assert_called_once_with('asd')
        mock_report.assert_called_once_with()
