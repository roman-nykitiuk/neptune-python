from django.db.models import Count
from django.test import TestCase
from django.core.management import call_command

from device.models import Specialty, Category, Product, Manufacturer


class AddDefaultDeviceCategoriesCommandTestCase(TestCase):
    def run_command_and_assert(self):
        call_command('add_default_device_categories')
        self.assertEqual(Specialty.objects.count(), 4)
        self.assertEqual(Category.objects.count(), 11)
        self.assertTupleEqual(
            tuple(Specialty.objects.annotate(categories_count=Count('category'))
                           .values_list('name', 'categories_count').order_by('name')),
            (('Interventional Cardiology', 2),
             ('Neuromodulation', 2),
             ('Orthopedic', 3),
             ('Structural Heart', 4))
        )

    def test_command_multiple_runs(self):
        self.run_command_and_assert()
        self.run_command_and_assert()


class ImportProductCommandTestCase(TestCase):
    def run_command_and_assert(self):
        call_command('import_products', '--file_path=device/tests/devices-data.xls')
        self.assertEqual(Manufacturer.objects.count(), 2)
        self.assertCountEqual(Manufacturer.objects.all().values_list('name',), (
            ('Medtronic',),
            ('Biotronik',)
        ))

        self.assertEqual(Specialty.objects.count(), 2)
        self.assertEqual(Category.objects.count(), 3)

        self.assertEqual(Product.objects.count(), 4)
        self.assertCountEqual(
            Product.objects.all().values_list('manufacturer__name', 'name', 'model_number', 'category__specialty__name',
                                              'category__name', 'enabled'),
            (
                ('Medtronic', 'Sensia', 'SESR01', 'Cardiac Rhythm Management', 'VVI Pacemakers', True),
                ('Biotronik', 'Etrinsa*', '394936', 'Cardiac Rhythm Management', 'VVI Pacemakers', False),
                ('Medtronic', 'Accolade*', 'L311', 'Cardiac Rhythm Management', 'DDD Pacemakers', True),
                ('Medtronic', 'Resolute Integrity', 'Resolute Integrity', 'Interventional Cardiology',
                 'DDD Pacemakers', True),
            )
        )

    def test_command_multiple_runs(self):
        self.run_command_and_assert()
        self.run_command_and_assert()
