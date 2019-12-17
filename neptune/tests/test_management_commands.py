from unittest.mock import Mock

from django.test import TestCase

from neptune.management.commands.import_data import ImportCommand


class ImportDataCommandTestCase(TestCase):
    def test_import_data_must_be_implemented(self):
        import_command = ImportCommand()
        import_command.load_data = Mock()
        with self.assertRaises(NotImplementedError):
            import_command.handle(file_path='data_file_path')
