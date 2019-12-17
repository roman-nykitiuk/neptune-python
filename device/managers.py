from django.db.models import Count, Q, QuerySet, Prefetch

from hospital.constants import BULK_PURCHASE
from price.constants import ON_DOCTOR_ORDER, PRE_DOCTOR_ORDER, UNIT_COST, SYSTEM_COST
from price.models import Discount


class ProductQuerySet(QuerySet):
    def unused_bulk_items_count_by_client(self, client):
        return self.filter(clientprice__client=client).annotate(
            bulk=Count('device__item', filter=Q(device__client=client,
                                                device__item__is_used=False,
                                                device__item__purchase_type=BULK_PURCHASE)),
        )

    def prefetch_features(self):
        from device.models import Feature

        return self.prefetch_related(
            Prefetch(
                'feature_set', to_attr='features',
                queryset=Feature.objects.filter(value__isnull=False)
                                .order_by('category_feature_id')
                                .select_related('shared_image', 'category_feature__shared_image')
            )
        )

    def prefetch_price_with_discounts(self, client, discount_apply_types=[ON_DOCTOR_ORDER, PRE_DOCTOR_ORDER]):
        discounts_queryset = Discount.objects.filter(
            apply_type__in=discount_apply_types
        ).order_by('order').select_related('shared_image')

        return self.prefetch_related(
            Prefetch(
                'clientprice_set', to_attr='client_prices',
                queryset=client.clientprice_set.prefetch_related(
                    Prefetch(
                        'discount_set',
                        queryset=discounts_queryset.filter(cost_type=UNIT_COST),
                        to_attr='unit_discounts'
                    ),
                    Prefetch(
                        'discount_set',
                        queryset=discounts_queryset.filter(cost_type=SYSTEM_COST),
                        to_attr='system_discounts'
                    )
                ),
            )
        )
