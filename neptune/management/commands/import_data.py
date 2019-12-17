import pandas as pd
import sys
from django.core.management import BaseCommand


class ImportCommand(BaseCommand):
    options = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = None

    def add_arguments(self, parser):
        parser.add_argument('--file_path', default='data.xls')

    def load_data(self, file_path):
        try:
            self.data = pd.read_excel(file_path, **self.options)
        except FileNotFoundError:
            print(f'No such file {file_path}')
            sys.exit(1)

    def handle(self, *args, **options):
        self.load_data(options['file_path'])
        self.import_data()

    def import_data(self):
        raise NotImplementedError()
