from datetime import datetime
from factory import DjangoModelFactory, Faker, SubFactory, post_generation

from device.factories import ProductFactory
from hospital.factories import AccountFactory
from order.models import Preference, Order, Question, Questionnaire


class QuestionFactory(DjangoModelFactory):
    class Meta:
        model = Question

    name = Faker('name')


class PreferenceFactory(DjangoModelFactory):
    class Meta:
        model = Preference

    name = Faker('name')

    @post_generation
    def questions(self, create, extracted, **kwargs):
        if extracted:
            for question in extracted:
                Questionnaire.objects.create(question=question, preference=self)


class OrderFactory(DjangoModelFactory):
    class Meta:
        model = Order

    product = SubFactory(ProductFactory)
    procedure_datetime = datetime.now()
    physician = SubFactory(AccountFactory)

    @post_generation
    def preference_questions(self, create, extracted, **kwargs):
        if extracted:
            self.preference_questions.set(extracted)
