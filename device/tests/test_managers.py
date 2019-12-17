from django.test import TestCase

from device.factories import ProductFactory, FeatureFactory
from device.models import Product
from hospital.factories import ClientFactory, ItemFactory, DeviceFactory
from price.constants import UNIT_COST, SYSTEM_COST
from price.factories import ClientPriceFactory, DiscountFactory


class ProductQuerySetTestCase(TestCase):
    def setUp(self):
        self.product_1, self.product_2 = ProductFactory.create_batch(2)

    def test_unused_bulk_items_count_by_client_queryset(self):
        client = ClientFactory()

        ClientPriceFactory(client=client, product=self.product_1, unit_cost=100, system_cost=120)
        ItemFactory.create_batch(3, device=client.device_set.get(product=self.product_1))
        ItemFactory.create_batch(2, device=DeviceFactory(product=self.product_2))
        products = Product.objects.unused_bulk_items_count_by_client(client)
        product = products.first()

        self.assertEqual(products.count(), 1)
        self.assertEqual(product, self.product_1)
        self.assertEqual(product.bulk, 3)

    def test_prefetch_features_queryset(self):
        feature_1 = FeatureFactory(product=self.product_1)
        feature_2, feature_3 = FeatureFactory.create_batch(2, product=self.product_2)

        products = Product.objects.prefetch_features().order_by('id')
        self.assertEqual(list(products), [self.product_1, self.product_2])
        self.assertCountEqual(products[0].features, [feature_1])
        self.assertCountEqual(products[1].features, [feature_2, feature_3])
        self.assertFalse(hasattr(self.product_1, 'features'))
        self.assertFalse(hasattr(self.product_2, 'features'))

    def test_prefetch_price_with_discounts(self):
        client_1, client_2 = ClientFactory.create_batch(2)
        client_price_1 = ClientPriceFactory(product=self.product_1, client=client_1)
        client_price_2 = ClientPriceFactory(product=self.product_2, client=client_2)
        discount_1 = DiscountFactory(cost_type=UNIT_COST, client_price=client_price_1)
        discount_2 = DiscountFactory(cost_type=SYSTEM_COST, client_price=client_price_1)
        discount_3 = DiscountFactory(cost_type=SYSTEM_COST, client_price=client_price_2)
        ClientPriceFactory(product=self.product_1, client=ClientFactory())

        products = Product.objects.prefetch_price_with_discounts(client_1).order_by('id')
        self.assertEqual(list(products), [self.product_1, self.product_2])
        self.assertEqual(len(products[0].client_prices), 1)
        self.assertEqual(len(products[1].client_prices), 0)
        self.assertCountEqual(products[0].client_prices[0].unit_discounts, [discount_1])
        self.assertCountEqual(products[0].client_prices[0].system_discounts, [discount_2])

        products = Product.objects.prefetch_price_with_discounts(client_2).order_by('id')
        self.assertEqual(list(products), [self.product_1, self.product_2])
        self.assertEqual(len(products[0].client_prices), 0)
        self.assertEqual(len(products[1].client_prices), 1)
        self.assertCountEqual(products[1].client_prices[0].unit_discounts, [])
        self.assertCountEqual(products[1].client_prices[0].system_discounts, [discount_3])

        products = Product.objects.prefetch_price_with_discounts(ClientFactory()).order_by('id')
        self.assertEqual(list(products), [self.product_1, self.product_2])
        self.assertEqual(len(products[0].client_prices), 0)
        self.assertEqual(len(products[1].client_prices), 0)
