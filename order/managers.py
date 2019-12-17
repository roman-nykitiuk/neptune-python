from django.db.models import Count, QuerySet, F


class OrderQuerySet(QuerySet):
    def count_by_category(self):
        return self.values('product__category__id')\
                   .annotate(count=Count('id')) \
                   .values('count',
                           response_id=F('product__category__id'),
                           name=F('product__category__name'))

    def count_by_specialty(self):
        return self.values('product__category__specialty')\
                   .annotate(count=Count('id'))\
                   .values('count',
                           response_id=F('product__category__specialty__id'),
                           name=F('product__category__specialty__name'))
