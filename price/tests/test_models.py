from decimal import Decimal

from datetime import date, datetime, timedelta
from django.db import IntegrityError
from django.test import TestCase
from django_fsm import TransitionNotAllowed

from device.factories import ProductFactory, CategoryFactory, SpecialtyFactory
from hospital.constants import BULK_PURCHASE, CONSIGNMENT_PURCHASE
from hospital.models import Item
from price.factories import ClientPriceFactory, DiscountFactory, RebatableItemFactory, RebateFactory, TierFactory
from price.models import ClientPrice, RebatableItem, Discount
from price.constants import UNIT_COST, SYSTEM_COST, VALUE_DISCOUNT, ELIGIBLE_ITEM, REBATED_ITEM, MARKETSHARE, SPEND, \
    PURCHASED_UNITS, USED_UNITS, COMPLETE_REBATE, NEW_REBATE, PERCENT_DISCOUNT, POST_DOCTOR_ORDER, PRE_DOCTOR_ORDER, \
    ON_DOCTOR_ORDER
from hospital.factories import ClientFactory, ItemFactory, DeviceFactory
from tracker.factories import RepCaseFactory
from tracker.models import RepCase


class ClientPriceTestCase(TestCase):
    def setUp(self):
        self.client_price = ClientPriceFactory(product=ProductFactory(name='product', model_number='001'),
                                               client=ClientFactory(name='Central hospital'),
                                               unit_cost=18000, system_cost=9000)
        self.unit_cost_discount_1 = DiscountFactory(cost_type=UNIT_COST, order=1, client_price=self.client_price,
                                                    percent=15, name='Bulk', apply_type=PRE_DOCTOR_ORDER)
        self.unit_cost_discount_2 = DiscountFactory(cost_type=UNIT_COST, order=2, client_price=self.client_price,
                                                    percent=10, name='CCO')
        self.system_cost_discount_1 = DiscountFactory(cost_type=SYSTEM_COST, order=4, client_price=self.client_price,
                                                      percent=15, name='Bulk', apply_type=PRE_DOCTOR_ORDER)
        self.system_cost_discount_2 = DiscountFactory(cost_type=SYSTEM_COST, order=2, client_price=self.client_price,
                                                      percent=10, name='CCO')

    def test_client_price_to_string(self):
        self.assertEqual(
            str(self.client_price),
            'Central hospital: Unit Price=$18000 - System Price=$9000'
        )

    def test_price_type_and_device_unique_together(self):
        with self.assertRaises(IntegrityError):
            ClientPrice.objects.create(product=self.client_price.product, client=self.client_price.client)

    def test_discounts(self):
        self.assertCountEqual(self.client_price.unit_cost_discounts,
                              [self.unit_cost_discount_1, self.unit_cost_discount_2])
        self.assertCountEqual(self.client_price.system_cost_discounts,
                              [self.system_cost_discount_2, self.system_cost_discount_1])

    def test_redeem(self):
        today = datetime.utcnow().date()
        unit_cost_discount = DiscountFactory(cost_type=UNIT_COST, order=3, client_price=self.client_price,
                                             discount_type=VALUE_DISCOUNT, value=688.50, name='Repless',
                                             apply_type=ON_DOCTOR_ORDER)
        system_repless_discount = DiscountFactory(cost_type=SYSTEM_COST, order=2, client_price=self.client_price,
                                                  discount_type=PERCENT_DISCOUNT, percent=5, name='Repless',
                                                  apply_type=ON_DOCTOR_ORDER)

        item = Item(purchased_date=today, rep_case=RepCase(procedure_date=today), cost_type=UNIT_COST)
        redemption = self.client_price.redeem(self.client_price.unit_cost_discounts, item)
        self.maxDiff = None
        self.assertDictEqual(redemption, {
            'original_cost': 18000,
            'total_cost': Decimal('13081.50'),
            'point_of_sales_saving': Decimal('2218.50'),
            'redeemed_discounts': [
                {
                    'discount': self.unit_cost_discount_1,
                    'is_valid': True,
                    'value': Decimal('2700.00'),
                },
                {
                    'discount': self.unit_cost_discount_2,
                    'is_valid': True,
                    'value': Decimal('1530.00'),
                },
                {
                    'discount': unit_cost_discount,
                    'is_valid': True,
                    'value': Decimal('688.50'),
                },
            ]
        })

        item.cost_type = SYSTEM_COST
        redemption = self.client_price.redeem(self.client_price.system_cost_discounts, item)
        self.assertDictEqual(redemption, {
            'original_cost': 9000,
            'total_cost': Decimal('6502.50'),
            'point_of_sales_saving': Decimal('1350.00'),
            'redeemed_discounts': [
                {
                    'discount': system_repless_discount,
                    'is_valid': True,
                    'value': Decimal('450.00'),
                },
                {
                    'discount': self.system_cost_discount_2,
                    'is_valid': True,
                    'value': Decimal('900.00'),
                },
                {
                    'discount': self.system_cost_discount_1,
                    'is_valid': True,
                    'value': Decimal('1147.50'),
                },
            ]
        })

        system_repless_discount.end_date = date(2017, 5, 6)
        system_repless_discount.save()
        redemption = self.client_price.redeem(self.client_price.system_cost_discounts, item)
        self.assertDictEqual(redemption, {
            'original_cost': 9000,
            'total_cost': Decimal('6885.00'),
            'point_of_sales_saving': Decimal('900'),
            'redeemed_discounts': [
                {
                    'discount': system_repless_discount,
                    'is_valid': False,
                    'value': Decimal('450.00'),
                },
                {
                    'discount': self.system_cost_discount_2,
                    'is_valid': True,
                    'value': Decimal('900.00'),
                },
                {
                    'discount': self.system_cost_discount_1,
                    'is_valid': True,
                    'value': Decimal('1215.00'),
                },
            ]
        })


class DiscountTestCase(TestCase):
    def setUp(self):
        self.discount = DiscountFactory()

    def test_discount_to_string(self):
        self.assertEqual(str(self.discount), self.discount.name)

    def test_is_valid_property(self):
        self.assertFalse(self.discount.is_valid())

        today = datetime.now().date()
        self.discount.start_date = today + timedelta(days=5)
        self.assertFalse(self.discount.is_valid(purchased_date=today))

        discount = DiscountFactory(end_date=date(2018, 5, 6))
        self.assertFalse(discount.is_valid(purchased_date=today))

    def test_display_name(self):
        spring_discount = DiscountFactory(name='Spring bulk', discount_type=PERCENT_DISCOUNT, percent=10, value=20)
        autumn_discount = DiscountFactory(name='Autumn bulk', discount_type=VALUE_DISCOUNT, percent=10, value=20)
        self.assertEqual(spring_discount.display_name, 'Spring bulk -10%')
        self.assertEqual(autumn_discount.display_name, 'Autumn bulk -$20')


class RebatableItemTestCase(TestCase):
    def test_to_string(self):
        self.assertEqual(str(RebatableItemFactory(content_object=ProductFactory(name='Entrosa'))), 'product: Entrosa')
        self.assertEqual(str(RebatableItemFactory(content_object=CategoryFactory(name='CRT-D'))), 'category: CRT-D')
        self.assertEqual(str(RebatableItemFactory(content_object=SpecialtyFactory(name='IH'))), 'specialty: IH')

    def test_product_ids(self):
        specialty = SpecialtyFactory()
        category_1, category_2 = CategoryFactory.create_batch(2, specialty=specialty)
        product_1, product_2 = ProductFactory.create_batch(2, category=category_1)
        product_3, product_4 = ProductFactory.create_batch(2, category=category_2)

        self.assertCountEqual(RebatableItemFactory(content_object=product_1).product_ids,
                              [product_1.id])
        self.assertCountEqual(RebatableItemFactory(content_object=category_1).product_ids,
                              [product_1.id, product_2.id])
        self.assertCountEqual(RebatableItemFactory(content_object=category_2).product_ids,
                              [product_3.id, product_4.id])
        self.assertCountEqual(RebatableItemFactory(content_object=specialty).product_ids,
                              [product_1.id, product_2.id, product_3.id, product_4.id])
        self.assertCountEqual(RebatableItemFactory(content_object=ClientFactory()).product_ids, [])


class RebateTestCase(TestCase):
    def setUp(self):
        self.rebate = RebateFactory(name='Q3 bulk rebate', start_date=date(2018, 7, 1), end_date=date(2018, 9, 30))
        self.category = CategoryFactory()
        self.product_1, self.product_2 = ProductFactory.create_batch(2, category=self.category,
                                                                     manufacturer=self.rebate.manufacturer)
        self.rebate_item_1 = RebatableItemFactory(content_object=self.product_1,
                                                  rebate=self.rebate, item_type=ELIGIBLE_ITEM)
        self.rebate_item_2 = RebatableItemFactory(content_object=self.category,
                                                  rebate=self.rebate, item_type=REBATED_ITEM)

    def test_to_string(self):
        self.assertEqual(str(self.rebate), 'Q3 bulk rebate: 2018-07-01 - 2018-09-30')

    def test_eligible_items(self):
        self.assertCountEqual(self.rebate.eligible_items, [self.rebate_item_1])

    def test_rebated_items(self):
        self.assertCountEqual(self.rebate.rebated_items, [self.rebate_item_2])

    def test_rebatable_product_ids(self):
        self.assertCountEqual(self.rebate.rebatable_product_ids(self.rebate.eligible_items), [self.product_1.id])
        self.assertCountEqual(self.rebate.rebatable_product_ids(self.rebate.rebated_items),
                              [self.product_1.id, self.product_2.id])
        self.assertCountEqual(self.rebate.rebatable_product_ids(RebatableItem.objects.none()), [])

    def test_get_device_items(self):
        self.assertCountEqual(self.rebate.get_device_items(self.rebate.rebated_items), [])
        self.assertCountEqual(self.rebate.get_device_items(self.rebate.eligible_items), [])

        item_1 = ItemFactory(device=DeviceFactory(client=self.rebate.client, product=self.product_1),
                             purchased_date=date(2018, 7, 16), is_used=False, purchase_type=BULK_PURCHASE)
        item_2 = ItemFactory(device=DeviceFactory(client=self.rebate.client, product=self.product_2),
                             purchased_date=date(2018, 7, 31), is_used=True, purchase_type=BULK_PURCHASE)
        ItemFactory(device=DeviceFactory(client=self.rebate.client, product=ProductFactory()),
                    purchased_date=date(2018, 7, 16), is_used=False, purchase_type=CONSIGNMENT_PURCHASE)
        ItemFactory(device=item_2.device,
                    purchased_date=date(2017, 12, 31), is_used=False, purchase_type=CONSIGNMENT_PURCHASE)

        self.assertCountEqual(self.rebate.get_device_items(self.rebate.eligible_items), [item_1])
        self.assertCountEqual(self.rebate.get_device_items(self.rebate.rebated_items), [item_1, item_2])
        self.assertCountEqual(self.rebate.get_device_items(RebatableItem.objects.none()), [item_1, item_2])


class RebateStatusTransitionTestCase(TestCase):
    def setUp(self):
        client = ClientFactory()
        product = ProductFactory()
        self.discount_1 = DiscountFactory(name='CCO', discount_type=PERCENT_DISCOUNT, percent=10, cost_type=UNIT_COST,
                                          order=1, apply_type=ON_DOCTOR_ORDER)
        self.discount_2 = DiscountFactory(name='Bulk', discount_type=VALUE_DISCOUNT, value=20, cost_type=SYSTEM_COST,
                                          order=1, apply_type=PRE_DOCTOR_ORDER)
        self.client_price = ClientPriceFactory(client=client, product=product, unit_cost=100, system_cost=120,
                                               discounts=[self.discount_1, self.discount_2])
        device = client.device_set.get(product=product)
        today = datetime.utcnow().date()
        self.item_1 = ItemFactory(device=device, cost_type=UNIT_COST,
                                  rep_case=RepCaseFactory(procedure_date=today),
                                  is_used=True, discounts=[self.discount_1])
        self.item_2, self.item_3 = ItemFactory.create_batch(2, device=device, cost_type=SYSTEM_COST, is_used=False,
                                                            discounts=[self.discount_2], purchased_date=today)

        self.rebate = RebateFactory(client=client, manufacturer=product.manufacturer)
        RebatableItemFactory(rebate=self.rebate, item_type=REBATED_ITEM, content_object=product)
        TierFactory(rebate=self.rebate, tier_type=SPEND, discount_type=PERCENT_DISCOUNT, percent=10, order=2)
        TierFactory(rebate=self.rebate, tier_type=PURCHASED_UNITS, discount_type=VALUE_DISCOUNT, value=20,
                    lower_bound=2, upper_bound=10, order=2)
        TierFactory(rebate=self.rebate, tier_type=PURCHASED_UNITS, discount_type=VALUE_DISCOUNT, value=50,
                    lower_bound=11, upper_bound=100, order=2)

    def test_transition_apply(self):
        self.assertEqual(self.rebate.status, NEW_REBATE)
        self.assertEqual(self.item_1.cost, 90)
        self.assertEqual(self.item_2.cost, 100)
        self.assertEqual(self.item_3.cost, 100)
        self.assertEqual(Discount.objects.count(), 2)

        self.rebate.apply()
        self.rebate.save()

        self.item_1.refresh_from_db()
        self.item_2.refresh_from_db()
        self.item_3.refresh_from_db()
        self.rebate.refresh_from_db()
        self.client_price.refresh_from_db()

        self.assertEqual(self.rebate.status, COMPLETE_REBATE)
        self.assertEqual(Discount.objects.count(), 6)
        unit_cost_discounts = Discount.objects.filter(apply_type=POST_DOCTOR_ORDER, cost_type=UNIT_COST)
        discount_3 = unit_cost_discounts.get(discount_type=PERCENT_DISCOUNT)
        discount_4 = unit_cost_discounts.get(discount_type=VALUE_DISCOUNT)
        system_cost_discounts = Discount.objects.filter(apply_type=POST_DOCTOR_ORDER, cost_type=SYSTEM_COST)
        discount_5 = system_cost_discounts.get(discount_type=PERCENT_DISCOUNT)
        discount_6 = system_cost_discounts.get(discount_type=VALUE_DISCOUNT)

        self.assertEqual(discount_3.percent, 10)
        self.assertEqual(discount_4.value, 20)
        self.assertEqual(discount_5.percent, 10)
        self.assertEqual(discount_6.value, 20)
        self.assertCountEqual(self.rebate.discount_set.all(), [discount_3, discount_4, discount_5, discount_6])
        self.assertCountEqual(self.client_price.discounts(UNIT_COST), [self.discount_1, discount_3, discount_4])
        self.assertCountEqual(self.client_price.discounts(SYSTEM_COST), [self.discount_2, discount_5, discount_6])

        self.assertCountEqual(self.item_1.discounts.all(), [self.discount_1, discount_3, discount_4])
        self.assertCountEqual(self.item_2.discounts.all(), [self.discount_2, discount_5, discount_6])
        self.assertCountEqual(self.item_3.discounts.all(), [self.discount_2, discount_5, discount_6])
        self.assertEqual(self.item_1.cost, 61)
        self.assertEqual(self.item_2.cost, 70)
        self.assertEqual(self.item_3.cost, 70)

        self.assertRaises(TransitionNotAllowed, self.rebate.apply)

    def test_transition_unapply(self):
        self.rebate.apply()
        self.rebate.unapply()
        self.rebate.save()

        self.item_1.refresh_from_db()
        self.item_2.refresh_from_db()
        self.item_3.refresh_from_db()
        self.rebate.refresh_from_db()
        self.client_price.refresh_from_db()

        self.assertEqual(self.rebate.status, NEW_REBATE)
        self.assertEqual(self.item_1.cost, 90)
        self.assertEqual(self.item_2.cost, 100)
        self.assertEqual(self.item_3.cost, 100)
        self.assertCountEqual(Discount.objects.all(), [self.discount_1, self.discount_2])

        self.assertRaises(TransitionNotAllowed, self.rebate.unapply)


class TierTestCase(TestCase):
    def setUp(self):
        product = ProductFactory()
        manufacturer = product.manufacturer
        client = ClientFactory()
        device = DeviceFactory(client=client, product=product)
        item_1 = ItemFactory(device=device, cost=100, purchased_date=date(2018, 4, 1), is_used=False)
        item_2 = ItemFactory(device=device, cost=120, purchased_date=date(2018, 4, 1), is_used=True)
        item_3 = ItemFactory(device=DeviceFactory(client=client, product=ProductFactory(manufacturer=manufacturer)),
                             cost=500, purchased_date=date(2018, 12, 24), is_used=False)
        ItemFactory(device=device, cost=100, purchased_date=date(2017, 12, 23), is_used=True)

        self.rebate = RebateFactory(client=client, manufacturer=manufacturer,
                                    start_date=date(2018, 1, 1), end_date=date(2018, 12, 31))
        self.tier = TierFactory(upper_bound=30, tier_type=MARKETSHARE, rebate=self.rebate)
        RebatableItemFactory(rebate=self.rebate, item_type=REBATED_ITEM, content_object=product)

        self.eligible_purchased_items = self.rebate.get_device_items(self.rebate.eligible_items)
        self.assertCountEqual(self.eligible_purchased_items, [item_1, item_2, item_3])

        self.rebated_purchased_items = self.rebate.get_device_items(self.rebate.rebated_items)
        self.assertCountEqual(self.rebated_purchased_items, [item_1, item_2])

    def test_to_string(self):
        self.assertEqual(str(self.tier), 'Marketshare in range (0, 30)')

    def test_spend(self):
        self.assertEqual(self.tier.spend(self.eligible_purchased_items), 720)

    def test_purchased_units(self):
        self.assertEqual(self.tier.purchased_units(self.eligible_purchased_items), 3)

    def test_used_units(self):
        self.assertEqual(self.tier.used_units(self.eligible_purchased_items), 1)

    def test_marketshare(self):
        self.assertEqual(self.tier.marketshare(self.eligible_purchased_items), 100)
        ItemFactory.create_batch(3, device=DeviceFactory(client=self.rebate.client, product=ProductFactory()),
                                 cost=160, purchased_date=date(2018, 12, 23), is_used=True)
        self.assertEqual(self.tier.marketshare(self.eligible_purchased_items), 60)

        self.rebate.client = ClientFactory()
        self.rebate.save()
        self.assertEqual(self.tier.marketshare(RebatableItem.objects.none()), 0)

    def test_is_valid(self):
        self.assertFalse(self.tier.is_valid(self.eligible_purchased_items))
        tier = TierFactory(lower_bound=31, upper_bound=100, tier_type=MARKETSHARE, rebate=self.rebate)
        self.assertTrue(tier.is_valid(self.eligible_purchased_items))

        tier_1 = TierFactory(lower_bound=300, upper_bound=600, tier_type=SPEND, rebate=self.rebate)
        tier_2 = TierFactory(lower_bound=720, upper_bound=720, tier_type=SPEND, rebate=self.rebate)
        self.assertFalse(tier_1.is_valid(self.eligible_purchased_items))
        self.assertTrue(tier_2.is_valid(self.eligible_purchased_items))

        tier_1 = TierFactory(lower_bound=0, upper_bound=2, tier_type=PURCHASED_UNITS, rebate=self.rebate)
        tier_2 = TierFactory(lower_bound=2, upper_bound=None, tier_type=PURCHASED_UNITS, rebate=self.rebate)
        self.assertFalse(tier_1.is_valid(self.eligible_purchased_items))
        self.assertTrue(tier_2.is_valid(self.eligible_purchased_items))

        tier_1 = TierFactory(lower_bound=11, upper_bound=100, tier_type=USED_UNITS, rebate=self.rebate)
        tier_2 = TierFactory(lower_bound=1, upper_bound=10, tier_type=USED_UNITS, rebate=self.rebate)
        self.assertFalse(tier_1.is_valid(self.eligible_purchased_items))
        self.assertTrue(tier_2.is_valid(self.eligible_purchased_items))
