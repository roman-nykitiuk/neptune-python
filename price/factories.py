from factory import DjangoModelFactory, SubFactory, fuzzy, faker, post_generation

from device.factories import ProductFactory, ManufacturerFactory
from hospital.factories import ClientFactory
from price.constants import REBATED_ITEM
from price.models import COST_TYPES


class ClientPriceFactory(DjangoModelFactory):
    class Meta:
        model = 'price.ClientPrice'

    product = SubFactory(ProductFactory)
    client = SubFactory(ClientFactory)
    unit_cost = fuzzy.FuzzyDecimal(0, 100000)
    system_cost = fuzzy.FuzzyDecimal(0, 100000)

    @post_generation
    def discounts(self, create, extracted, **kwargs):
        if extracted:
            self.discount_set.set(extracted)


class DiscountFactory(DjangoModelFactory):
    class Meta:
        model = 'price.Discount'

    name = faker.Faker('name')
    order = fuzzy.FuzzyInteger(1)
    percent = fuzzy.FuzzyDecimal(0, 100.00)
    cost_type = fuzzy.FuzzyChoice([x[0] for x in COST_TYPES])
    client_price = SubFactory(ClientPriceFactory)


class RebateFactory(DjangoModelFactory):
    class Meta:
        model = 'price.Rebate'

    name = faker.Faker('name')
    client = SubFactory(ClientFactory)
    manufacturer = SubFactory(ManufacturerFactory)


class RebatableItemFactory(DjangoModelFactory):
    class Meta:
        model = 'price.RebatableItem'

    content_object = SubFactory(ProductFactory)
    item_type = REBATED_ITEM
    rebate = SubFactory(RebateFactory)


class TierFactory(DjangoModelFactory):
    class Meta:
        model = 'price.Tier'

    rebate = SubFactory(RebateFactory)
