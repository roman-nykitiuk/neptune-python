from import_export import resources

from device.models import Product


class ProductResource(resources.ModelResource):
    class Meta:
        model = Product
        fields = ('name', 'level')
