from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from device.models import Product
from hospital.models import Account
from price.models import COST_TYPES, UNIT_COST
from order.managers import OrderQuerySet
ORDER_NEW = 1
ORDER_PENDING = 2
ORDER_COMPLETE = 3
ORDER_CANCELLED = 4

ORDER_STATUSES = (
    (ORDER_NEW, _('New')),
    (ORDER_PENDING, _('Pending')),
    (ORDER_COMPLETE, _('Complete')),
    (ORDER_CANCELLED, _('Cancelled')),
)


class Question(models.Model):
    name = models.CharField(_('Question'), max_length=255, unique=True)

    def __str__(self):
        return self.name


class Preference(models.Model):
    name = models.CharField(_('Name'), max_length=255, default='Default')
    questions = models.ManyToManyField(Question, through='order.Questionnaire')
    client = models.ForeignKey('hospital.Client', null=True, blank=True, on_delete=models.CASCADE)
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE,
        limit_choices_to=Q(app_label='device') & (Q(model__in=('specialty', 'category'))),
        null=True, blank=True,
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        unique_together = ('client', 'content_type', 'object_id')

    def __str__(self):
        return self.name

    @staticmethod
    def _retrieve_preferences(client=None, model_object=None):
        kwargs = dict(client=client, content_type=None, object_id=None)
        if model_object:
            content_type = ContentType.objects.get_for_model(model_object)
            kwargs.update(dict(content_type=content_type, object_id=model_object.id))
        return Preference.objects.filter(**kwargs)

    @staticmethod
    def get_preferences_by_product_client(product, client):
        cases = (
            (client, product.category),
            (client, product.category.specialty),
            (None, product.category),
            (None, product.category.specialty),
            (client,),
            (),
        )
        for case in cases:
            preference = Preference._retrieve_preferences(*case)
            if preference.exists():
                return preference.first().questions.all()
        return Question.objects.none()


class Questionnaire(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    preference = models.ForeignKey(Preference, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('preference', 'question')


class Order(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    procedure_datetime = models.DateTimeField()
    physician = models.ForeignKey(Account, on_delete=models.CASCADE)
    preference_questions = models.ManyToManyField(Question)
    status = models.PositiveSmallIntegerField(choices=ORDER_STATUSES, default=ORDER_NEW)
    cost_type = models.PositiveSmallIntegerField(choices=COST_TYPES, default=UNIT_COST)
    discounts = JSONField(default={})

    objects = OrderQuerySet.as_manager()

    def __str__(self):
        return f'{self.product} at {self.procedure_datetime}'
