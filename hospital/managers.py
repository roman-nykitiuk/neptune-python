from django.db.models import QuerySet, Sum, Count, F, Avg, FloatField
from django.db.models.functions import TruncMonth


class ItemQuerySet(QuerySet):
    def used_by_client(self, client):
        return self.filter(rep_case__client=client)

    def used_by_physician(self, physician):
        return self.used_by_client(physician.client).filter(rep_case__physician=physician)

    def used_in_period(self, year, month=None):
        queryset = self.filter(rep_case__procedure_date__year=year)
        if month:
            queryset = queryset.filter(rep_case__procedure_date__month=month)
        return queryset

    def marketshare(self):
        return self.values('device__product__manufacturer').annotate(
            spend=Sum('cost', output_field=FloatField()),
            units=Count('cost'),
            app=Avg('cost', output_field=FloatField())
        ).values(
            'spend', 'units', 'app',
            manufacturer_short_name=F('device__product__manufacturer__short_name'),
            manufacturer_name=F('device__product__manufacturer__name'),
            manufacturer_id=F('device__product__manufacturer__id'),
            manufacturer_image=F('device__product__manufacturer__image'),
        )

    def physician_app(self):
        return self.values('rep_case__physician').annotate(
            app=Avg('cost', output_field=FloatField())
        ).values(
            'app',
            physician_id=F('rep_case__physician__id'),
            physician_name=F('rep_case__physician__user__name'),
        )

    def saving_by_categories(self):
        return self.values('device__product__category').annotate(
            saving=Sum('saving'),
            spend=Sum('cost')
        ).values(
            'saving', 'spend',
            category_id=F('device__product__category__id'),
            category_name=F('device__product__category__name'),
        )

    def savings_by_month(self, year):
        return self.used_in_period(year)\
            .annotate(month=TruncMonth('rep_case__procedure_date')).values('month')\
            .annotate(savings=Sum('saving'), spend=Sum('cost')).values('month', 'savings', 'spend')
