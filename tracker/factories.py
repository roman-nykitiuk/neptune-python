from factory import DjangoModelFactory, Faker, SubFactory, post_generation

from device.factories import CategoryFactory
from hospital.factories import ClientFactory, AccountFactory
from tracker.models import RepCase, PurchasePrice


class RepCaseFactory(DjangoModelFactory):
    class Meta:
        model = RepCase

    client = SubFactory(ClientFactory)
    procedure_date = Faker('date')
    physician = SubFactory(AccountFactory)

    @post_generation
    def owners(self, create, extracted, **kwargs):
        if extracted:
            self.owners.set(extracted)

    @post_generation
    def items(self, create, extracted, **kwargs):
        if extracted:
            self.item_set.set(extracted)


class PurchasePriceFactory(DjangoModelFactory):
    class Meta:
        model = PurchasePrice

    category = SubFactory(CategoryFactory)
    client = SubFactory(ClientFactory)
    year = Faker('year')
