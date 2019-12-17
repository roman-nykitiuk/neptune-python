from django.db import IntegrityError
from django.test import TestCase

from device.factories import SpecialtyFactory, CategoryFactory, ProductFactory, ManufacturerFactory, FeatureFactory, \
    CategoryFeatureFactory
from device.models import Specialty, Category, Feature, CategoryFeature


class SpecialtyTestCase(TestCase):
    def test_to_string_returns_specialty_name(self):
        specialty = SpecialtyFactory()
        self.assertEqual(str(specialty), specialty.name)

    def test_unique_specialty_name(self):
        specialty = SpecialtyFactory()
        self.assertRaises(IntegrityError, Specialty.objects.create, name=specialty.name)


class CategoryTestCase(TestCase):
    def test_to_string_returns_category_name(self):
        category = CategoryFactory()
        self.assertEqual(str(category), category.name)

    def test_unique_category_name(self):
        category = CategoryFactory()
        self.assertRaises(IntegrityError, Category.objects.create, name=category.name)

    def test_get_all_parent_categories(self):
        category_1 = CategoryFactory()
        category_2 = CategoryFactory(parent=category_1)
        category_3 = CategoryFactory(parent=category_2)
        category_4 = CategoryFactory(parent=category_1)
        category_5 = CategoryFactory(parent=category_4)

        self.assertCountEqual(Category.get_all_parent_categories([category_3.id, category_5.id]),
                              [category_1, category_2, category_4])

    def test_get_all_parent_categories_with_circling_loop(self):
        category_1 = CategoryFactory()
        category_2 = CategoryFactory(parent=category_1)
        category_1.parent = category_2
        category_1.save()
        parent_categories = Category.get_all_parent_categories([category_2.id])
        self.assertCountEqual(parent_categories, [category_1, category_2])


class ProductTestCase(TestCase):
    def setUp(self):
        self.specialty = SpecialtyFactory(name='Structural Heart')
        self.product = ProductFactory(category=CategoryFactory(specialty=self.specialty))

    def test_to_string_returns_product_name(self):
        self.assertEqual(str(self.product), self.product.name)

    def test_specialty_property(self):
        self.assertEqual(self.product.specialty, self.specialty)

    def test_missing_category_features_property(self):
        category_features = CategoryFeatureFactory.create_batch(2, category=self.product.category)
        self.assertCountEqual(self.product.missing_category_features, category_features)

        FeatureFactory(product=self.product)
        FeatureFactory(product=self.product, category_feature=CategoryFeatureFactory())
        FeatureFactory(product=self.product, name=category_features[1])
        self.assertCountEqual(self.product.missing_category_features, category_features[0:1])

        FeatureFactory(product=self.product, name=category_features[0].name)
        self.assertEqual(self.product.missing_category_features.count(), 0)

    def test_remove_invalid_category_features(self):
        category_features = CategoryFeatureFactory.create_batch(2, category=self.product.category)
        for category_feature in category_features:
            FeatureFactory(product=self.product, name=category_feature.name)
        FeatureFactory(product=self.product)
        self.assertEqual(Feature.objects.count(), 3)
        self.assertEqual(CategoryFeature.objects.count(), 3)

        self.product.category = CategoryFactory()
        self.product.remove_invalid_category_features()
        self.assertEqual(Feature.objects.count(), 0)


class ManufacturerTestCase(TestCase):
    def setUp(self):
        self.manufacturer = ManufacturerFactory()

    def test_manufacturer_to_string(self):
        self.assertEqual(str(self.manufacturer), self.manufacturer.name)

    def test_rebatable_items(self):
        for model_name in ['product', 'category', 'specialty']:
            self.assertCountEqual(self.manufacturer.rebatable_items(model_name), [])

        specialty_1, specialty_2 = SpecialtyFactory.create_batch(2)
        category_1 = CategoryFactory(specialty=specialty_1)
        category_2, category_3 = CategoryFactory.create_batch(2, specialty=specialty_2)
        product_1 = ProductFactory(category=category_1, manufacturer=self.manufacturer)
        product_2 = ProductFactory(category=category_2, manufacturer=self.manufacturer)
        product_3 = ProductFactory(category=category_3, manufacturer=self.manufacturer)
        product_4 = ProductFactory(category=category_1, manufacturer=self.manufacturer)
        ProductFactory(category=category_3)

        self.assertCountEqual(self.manufacturer.rebatable_items('specialty'), [specialty_1, specialty_2])
        self.assertCountEqual(self.manufacturer.rebatable_items('category'), [category_1, category_2, category_3])
        self.assertCountEqual(self.manufacturer.rebatable_items('product'),
                              [product_1, product_2, product_3, product_4])
        self.assertCountEqual(self.manufacturer.rebatable_items('manufacturer'), [])

    def test_display_name(self):
        self.assertIsNone(self.manufacturer.short_name)
        self.assertEqual(self.manufacturer.display_name, self.manufacturer.name)

        self.manufacturer.short_name = 'MDT'
        self.assertEqual(self.manufacturer.display_name, 'MDT')


class CategoryFeatureTestCase(TestCase):
    def setUp(self):
        self.product = ProductFactory()
        self.category_feature = CategoryFeatureFactory(name='Network', category=self.product.category)

    def test_category_feature_to_string(self):
        self.assertEqual(str(self.category_feature), self.category_feature.name)

    def test_post_save_update_feature_name(self):
        feature = FeatureFactory(category_feature=self.category_feature,
                                 name=self.category_feature.name, product=self.product)
        self.assertEqual(feature.name, 'Network')

        self.category_feature.name = 'Wireless'
        self.category_feature.save()
        feature.refresh_from_db()
        self.assertEqual(feature.name, 'Wireless')


class FeatureTestCase(TestCase):
    def test_feature_to_string(self):
        feature = FeatureFactory(name='Dimension')
        self.assertEqual(str(feature), 'Dimension')

        category_feature = feature.category_feature
        self.assertEqual(category_feature.name, feature.name)

        category_feature.name = 'New dimension'
        category_feature.save()
        feature.refresh_from_db()
        self.assertEqual(str(feature), 'New dimension')
