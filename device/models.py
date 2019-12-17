from functools import partial

from django.db import models
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from device.constants import ProductLevel, MAX_SUB_CATEGORIES_LEVEL
from device.managers import ProductQuerySet
from neptune.models import SharedImage
from neptune.utils import make_imagefield_filepath


class Specialty(models.Model):
    name = models.CharField(_('Specialty'), unique=True, max_length=255)

    class Meta:
        verbose_name_plural = '  Specialties'

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(_('Device category'), max_length=255)
    specialty = models.ForeignKey(Specialty, on_delete=models.CASCADE, default=None)
    image = models.ImageField(_('Category image'), upload_to=partial(make_imagefield_filepath, 'categories'),
                              null=True, blank=True)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, related_name='sub_categories', null=True, blank=True)

    class Meta:
        verbose_name_plural = ' Categories'
        unique_together = ('name', 'specialty')

    def __str__(self):
        return self.name

    @classmethod
    def get_all_parent_categories(cls, category_ids):
        categories = Category.objects.filter(id__in=category_ids).all()
        sub_categories_level = 0
        all_parent_category_ids = []
        parent_categories = cls.get_parent_categories(categories)
        while (parent_categories.count() > 0) and (sub_categories_level < MAX_SUB_CATEGORIES_LEVEL):
            sub_categories_level += 1
            all_parent_category_ids += list(parent_categories.values_list('id', flat=True))
            parent_categories = cls.get_parent_categories(parent_categories)

        return cls.objects.filter(id__in=all_parent_category_ids).distinct().all()

    @classmethod
    def get_parent_categories(cls, categories):
        parent_ids = categories.exclude(parent__isnull=True).values_list('parent_id', flat=True).distinct()
        return cls.objects.filter(id__in=parent_ids).distinct().all()


class Manufacturer(models.Model):
    name = models.CharField(_('Manufacturer'), max_length=255)
    short_name = models.CharField(_('Short name'), max_length=16, null=True, blank=True)
    image = models.ImageField(upload_to=partial(make_imagefield_filepath, 'manufacturers'), null=True, blank=True)

    def __str__(self):
        return self.name

    @property
    def display_name(self):
        return self.short_name or self.name

    def rebatable_items(self, model_name):
        if model_name == 'product':
            return self.product_set.all()
        elif model_name == 'category':
            return Category.objects.filter(product__manufacturer=self).distinct().all()
        elif model_name == 'specialty':
            return Specialty.objects.filter(category__product__manufacturer=self).distinct().all()
        return []


class Product(models.Model):
    name = models.CharField(_('Device name'), max_length=255)
    image = models.ImageField(_('Product image'), upload_to=partial(make_imagefield_filepath, 'devices'),
                              null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.CASCADE, null=True, blank=False)
    level = models.PositiveSmallIntegerField('Product level',
                                             choices=ProductLevel.to_field_choices(),
                                             default=ProductLevel.default().value)
    model_number = models.CharField(_('Model number'), max_length=255, null=True, blank=False)
    enabled = models.BooleanField(_('Enabled'), default=True)

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name_plural = ' Products'

    def __str__(self):
        return self.name

    @property
    def specialty(self):
        return self.category.specialty

    @property
    def missing_category_features(self):
        all_category_features = self.category.categoryfeature_set.select_related('shared_image').all()
        existing_category_features_ids = self.feature_set.filter(category_feature__isnull=False) \
                                             .values_list('category_feature__id', flat=True)

        return all_category_features.exclude(id__in=existing_category_features_ids)

    def remove_invalid_category_features(self):
        self.feature_set.filter(category_feature__isnull=False) \
                        .exclude(category_feature__category=self.category) \
                        .delete()


class CategoryFeature(models.Model):
    name = models.CharField(_('Feature name'), max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    shared_image = models.ForeignKey(SharedImage, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.feature_set.update(name=self.name)


class Feature(models.Model):
    name = models.CharField(_('Feature name'), max_length=255, null=True, blank=False)
    value = models.CharField(_('Feature value'), max_length=255, null=True, blank=True)
    category_feature = models.ForeignKey(CategoryFeature, on_delete=models.CASCADE, null=True, blank=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=False)
    shared_image = models.ForeignKey(SharedImage, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        unique_together = ('name', 'product')

    def __str__(self):
        return self.category_feature.name if self.category_feature else self.name

    @property
    def icon(self, ):
        shared_image = self.category_feature.shared_image if self.category_feature else self.shared_image
        return mark_safe(f'<img src="{shared_image.image.url}" />')

    def save(self, *args, **kwargs):
        if self.id or self.value:
            category_feature = CategoryFeature.objects.get_or_create(category=self.product.category,
                                                                     name=self.name)[0]
            if category_feature.shared_image != self.shared_image:
                category_feature.shared_image = self.shared_image
                category_feature.save()
                category_feature.feature_set.exclude(id=self.id).update(shared_image=category_feature.shared_image)
            self.category_feature = category_feature
            super().save(*args, **kwargs)
