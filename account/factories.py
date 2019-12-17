from factory import DjangoModelFactory, Faker
from django.contrib.auth.hashers import make_password

from account.models import User


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    name = Faker('name')
    email = Faker('email')
    password = make_password('password1')
