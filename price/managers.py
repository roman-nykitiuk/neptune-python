from django.db.models import QuerySet

from hospital.constants import BULK_PURCHASE
from price.constants import PRE_DOCTOR_ORDER


class DiscountQuerySet(QuerySet):
    def available_in_client_inventory(self, client):
        return self.filter(
            apply_type=PRE_DOCTOR_ORDER,
            client_price__client=client,
            item__purchase_type=BULK_PURCHASE,
            item__is_used=False,
        ).distinct()

    def to_client_prices_dict(self):
        discounts = self.select_related('client_price')

        client_prices = {}
        for discount in discounts:
            client_price = client_prices.setdefault(discount.client_price.id, {})
            discount_list = client_price.setdefault(discount.cost_type, [])
            discount_list.append(discount)
        return client_prices
