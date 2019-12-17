from factory import DjangoModelFactory, Faker, SubFactory, Sequence, post_generation

from account.factories import UserFactory
from device.factories import ProductFactory
from hospital.converter import int_to_b32


class ClientFactory(DjangoModelFactory):
    class Meta:
        model = 'hospital.Client'

    name = Faker('company')
    street = Faker('street_address')
    city = Faker('city')
    state = Faker('state')
    country = Faker('country_code')


class DeviceFactory(DjangoModelFactory):
    class Meta:
        model = 'hospital.Device'

    client = SubFactory(ClientFactory)
    product = SubFactory(ProductFactory)
    hospital_number = Faker('ean8')


class RoleFactory(DjangoModelFactory):
    class Meta:
        model = 'hospital.Role'

    name = Faker('name')
    priority = Faker('random_int', min=1)


class AccountFactory(DjangoModelFactory):
    class Meta:
        model = 'hospital.Account'

    user = SubFactory(UserFactory)
    client = SubFactory(ClientFactory)
    role = SubFactory(RoleFactory)

    @post_generation
    def specialties(self, create, extracted, **kwargs):
        if extracted:
            self.specialties.set(extracted)
            self.save()


class ItemFactory(DjangoModelFactory):
    class Meta:
        model = 'hospital.Item'

    device = SubFactory(DeviceFactory)
    serial_number = Sequence(lambda n: f'SERIAL-{int_to_b32(n, 5)}')
    expired_date = Faker('future_date')
    purchased_date = Faker('past_date')
    cost = Faker('pydecimal', left_digits=3, right_digits=2, positive=True)

    @post_generation
    def discounts(self, create, extracted, **kwargs):
        if extracted:
            self.discounts.set(extracted)
            self.update_cost(extracted)
            self.save()
