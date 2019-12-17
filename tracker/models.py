from django.db import models
from django.db.models import Min, Max, Avg
from django.utils.translation import gettext_lazy as _

from device.constants import ProductLevel
from price.constants import COST_TYPES, UNIT_COST
from tracker.constants import CASE_STATUSES, NEW_CASE


class RepCase(models.Model):
    client = models.ForeignKey('hospital.Client', on_delete=models.CASCADE)
    owners = models.ManyToManyField('hospital.Account')
    physician = models.ForeignKey('hospital.Account', on_delete=models.CASCADE,
                                  null=True, blank=False, related_name='rep_cases')
    procedure_date = models.DateField()
    status = models.PositiveSmallIntegerField(choices=CASE_STATUSES, default=NEW_CASE)

    def __str__(self):
        return f'{self.get_status_display()} case at {self.client} on {self.procedure_date}'


class PurchasePrice(models.Model):
    category = models.ForeignKey('device.Category', on_delete=models.CASCADE)
    client = models.ForeignKey('hospital.Client', on_delete=models.CASCADE)
    year = models.IntegerField()
    level = models.PositiveSmallIntegerField(_('Device level'),
                                             choices=ProductLevel.to_field_choices(),
                                             default=ProductLevel.default().value)
    cost_type = models.PositiveSmallIntegerField(_('Cost type'), choices=COST_TYPES, default=UNIT_COST)
    avg = models.DecimalField(_('Average purchase price'), max_digits=20, decimal_places=2, default=0)
    min = models.DecimalField(_('Lowest purchase price'), max_digits=20, decimal_places=2, null=True, blank=True)
    max = models.DecimalField(_('Highest purchase price'), max_digits=20, decimal_places=2, default=0)

    class Meta:
        unique_together = ('category', 'client', 'year', 'level', 'cost_type')

    def __str__(self):
        return (f'{self.category} - {self.client} - {self.get_level_display()} '
                f'- {self.get_cost_type_display()}: ${self.avg}')

    @classmethod
    def update(cls, category, client, year, level, cost_type):
        purchase_price = PurchasePrice.objects.get_or_create(
            category=category,
            client=client,
            year=year,
            level=level,
            cost_type=cost_type,
        )[0]
        purchase_price.update_prices()

    def update_prices(self):
        aggregated_price = self.client.items.filter(
            device__product__category=self.category,
            device__product__level=self.level,
            is_used=True, cost_type=self.cost_type,
            cost__gt=0,
            rep_case__procedure_date__year=self.year
        ).aggregate(min=Min('cost'), max=Max('cost'), avg=Avg('cost'))

        self.avg = aggregated_price.get('avg') or 0
        self.min = aggregated_price.get('min')
        self.max = aggregated_price.get('max') or 0
        self.save()
