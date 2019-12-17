from django.core.management import BaseCommand

from device.factories import SpecialtyFactory, CategoryFactory

DEFAULT_SPECIALTIES = (
    ('Interventional Cardiology', (
        'Drug Eluting Stents',
        'Bare Metal Stents',
    )),
    ('Structural Heart', (
        'TAVR Implant System',
        'TAVR Valve',
        'TAVR Delivery System',
        'TAVR Loading System',
    )),
    ('Neuromodulation', (
        'Spinal Cord Stimulation Device',
        'Spinal Cord Stimulation Lead',
    )),
    ('Orthopedic', (
        'Total Knee System',
        'Total Hip System',
        '​Spinal Implant System',
    ))
)


class Command(BaseCommand):
    help = 'Add default default categories and specialties'

    def handle(self, *args, **options):
        for specialty, categories in DEFAULT_SPECIALTIES:
            self.add_specialty_with_categories(name=specialty,
                                               categories=categories)

    def add_specialty_with_categories(self, name, categories):
        specialty = SpecialtyFactory(name=name)
        for category in categories:
            CategoryFactory(name=category, specialty=specialty)
