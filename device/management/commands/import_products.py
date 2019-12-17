from device.models import Manufacturer, Specialty, Category, Product
from neptune.management.commands.import_data import ImportCommand


class Command(ImportCommand):
    help = 'Import manufacturers, specialties, device categories and products'
    options = {'sheet_name': 'Devices Details'}

    def import_data(self):
        imported_manufacturers = {}
        imported_specialties = {}

        for index, row in self.data.iterrows():
            row = (str(data).strip() for data in row)
            product_id, manufacturer_name, product_name, model_number, specialty_name, category_name, status = row
            enabled = status == 'Enabled'

            manufacturer_id = imported_manufacturers.setdefault(
                manufacturer_name,
                Manufacturer.objects.get_or_create(name=manufacturer_name)[0].id
            )
            imported_specialty = imported_specialties.setdefault(
                specialty_name,
                {
                    'id': Specialty.objects.get_or_create(name=specialty_name)[0].id,
                    'categories': {}
                }
            )
            category_id = imported_specialty['categories'].setdefault(
                category_name,
                Category.objects.get_or_create(name=category_name, specialty_id=imported_specialty['id'])[0].id
            )
            product_created = Product.objects.get_or_create(name=product_name, category_id=category_id,
                                                            manufacturer_id=manufacturer_id,
                                                            model_number=model_number, enabled=enabled)[1]
            print(f'Import product#{product_id} {product_name}: {"created" if product_created else "skipped"}')
