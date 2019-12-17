from factory import DjangoModelFactory, faker, SubFactory


class SpecialtyFactory(DjangoModelFactory):
    class Meta:
        model = 'device.Specialty'
        django_get_or_create = ('name',)

    name = faker.Faker('name')


class CategoryFactory(DjangoModelFactory):
    class Meta:
        model = 'device.Category'
        django_get_or_create = ('name',)

    name = faker.Faker('name')
    specialty = SubFactory(SpecialtyFactory)


class ManufacturerFactory(DjangoModelFactory):
    class Meta:
        model = 'device.Manufacturer'

    name = faker.Faker('name')


class ProductFactory(DjangoModelFactory):
    class Meta:
        model = 'device.Product'

    name = faker.Faker('name')
    category = SubFactory(CategoryFactory)
    manufacturer = SubFactory(ManufacturerFactory)
    model_number = str(faker.Faker('random_int'))


class CategoryFeatureFactory(DjangoModelFactory):
    class Meta:
        model = 'device.CategoryFeature'

    name = faker.Faker('name')
    category = SubFactory(CategoryFactory)


class FeatureFactory(DjangoModelFactory):
    class Meta:
        model = 'device.Feature'

    name = faker.Faker('name')
    value = str(faker.Faker('random_int'))
    product = SubFactory(ProductFactory)
