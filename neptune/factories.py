from factory import DjangoModelFactory, faker


class SharedImageFactory(DjangoModelFactory):
    class Meta:
        model = 'neptune.SharedImage'

    name = faker.Faker('name')
