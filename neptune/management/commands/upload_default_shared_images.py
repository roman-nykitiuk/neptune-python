from django.core.management import BaseCommand

from device.models import CategoryFeature
from neptune.management.commands.import_from_mysql import upload_shared_image
from price.models import Discount


class Command(BaseCommand):
    options = {}

    def handle(self, *args, **options):
        self.shared_images_for(model_class=CategoryFeature, upload_from='features')
        self.shared_images_for(model_class=Discount, upload_from='discounts')

    def shared_images_for(self, model_class, upload_from):
        names = model_class.objects.values_list('name', flat=True).distinct()

        for name in names:
            shared_image_name = f'{name}.png'
            upload_shared_image(shared_image_name, upload_from)
