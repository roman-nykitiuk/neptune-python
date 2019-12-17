from datetime import datetime
from django.test import TestCase

from device.factories import ProductFactory
from hospital.factories import ClientFactory
from order.factories import PreferenceFactory, OrderFactory, QuestionFactory
from order.models import Preference


class PreferenceTestCase(TestCase):
    def setUp(self):
        self.client = ClientFactory()
        self.product = ProductFactory()

    def test_preference_to_string(self):
        preference = PreferenceFactory(name='default preferences')
        self.assertEqual(str(preference), 'default preferences')

    def test_get_preferences_when_category_preferences_exist(self):
        question_1, question_2 = QuestionFactory.create_batch(2)
        PreferenceFactory(
            content_object=self.product.category, client=self.client,
            questions=[question_1, question_2]
        )
        PreferenceFactory(content_object=self.product.category)
        self.assertCountEqual(
            Preference.get_preferences_by_product_client(self.product, self.client),
            [question_1, question_2]
        )

    def test_get_preferences_when_specialty_preferences_exist(self):
        question_1, question_2 = QuestionFactory.create_batch(2)
        PreferenceFactory(
            content_object=self.product.category.specialty, client=self.client,
            questions=[question_1, question_2]
        )
        PreferenceFactory(content_object=self.product.category.specialty)
        self.assertCountEqual(
            Preference.get_preferences_by_product_client(self.product, self.client),
            [question_1, question_2]
        )

    def test_get_preferences_when_only_client_preference_exist(self):
        question = QuestionFactory()
        PreferenceFactory(client=self.client, content_object=None, questions=[question])
        product = ProductFactory()
        PreferenceFactory(client=ClientFactory())
        PreferenceFactory(client=self.client, content_object=product.category)
        PreferenceFactory(client=self.client, content_object=product.category.specialty)
        self.assertCountEqual(
            Preference.get_preferences_by_product_client(self.product, self.client),
            [question]
        )

    def test_get_common_preferences(self):
        question = QuestionFactory()
        PreferenceFactory(client=None, content_object=None, questions=[question])
        PreferenceFactory(client=ClientFactory())
        self.assertCountEqual(
            Preference.get_preferences_by_product_client(self.product, self.client),
            [question]
        )

    def test_get_preferences_when_has_category_but_not_client(self):
        question = QuestionFactory()
        PreferenceFactory(client=None, content_object=self.product.category, questions=[question])
        PreferenceFactory(client=self.client, content_object=None)
        self.assertCountEqual(
            Preference.get_preferences_by_product_client(self.product, self.client),
            [question]
        )

    def test_get_preferences_return_empty_list(self):
        PreferenceFactory(client=ClientFactory())
        self.assertCountEqual(
            Preference.get_preferences_by_product_client(self.product, self.client),
            []
        )


class OderTestCase(TestCase):
    def test_order_to_string(self):
        order = OrderFactory(product=ProductFactory(name='Pacemaker'),
                             procedure_datetime=datetime(2020, 1, 2, 3, 4, 5))
        self.assertEqual(str(order), 'Pacemaker at 2020-01-02 03:04:05')
