from datetime import datetime

from django import forms
from django.contrib import admin
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import Prefetch
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.functional import curry
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from easy_select2 import apply_select2

from import_export.admin import ImportExportModelAdmin

from device.forms import CategoryForm, ProductForm
from device.models import Category, Specialty, Product, Manufacturer, Feature, CategoryFeature
from device.resources import ProductResource
from hospital.constants import BULK_PURCHASE, CONSIGNMENT_PURCHASE
from hospital.models import Device, Item
from neptune.admin import AutoCompleteSearchAdminMixin
from price.models import ClientPrice, UNIT_COST, SYSTEM_COST, Discount
from tracker.models import RepCase


class SpecialtyAdmin(admin.ModelAdmin, AutoCompleteSearchAdminMixin):
    search_fields = ('name', 'category__name', 'category__product__name')

    list_display = ('specialty_name',)

    def specialty_name(self, obj):
        categories_url = reverse('admin:device_category_changelist')
        specialty_url = reverse('admin:device_specialty_change', args=(obj.id,))
        return format_html(f"""
            <a href='{categories_url}?specialty__id={obj.id}&parent__isnull=True'>{obj.name}</a>
            &nbsp;&nbsp;
            <a href='{specialty_url}'><img src='/static/admin/img/icon-changelink.svg' alt='Edit'></a>
        """)


class CategoryFeaturesInline(admin.TabularInline):
    model = CategoryFeature
    extra = 0
    fields = ('name', 'icon', 'shared_image')
    readonly_fields = ('icon',)

    def icon(self, feature):
        return mark_safe(f'<img src="{feature.shared_image.image.url}" />')


class CategoryAdmin(admin.ModelAdmin):
    form = CategoryForm
    inlines = (CategoryFeaturesInline,)
    list_display = ('category_name', 'parent', 'specialty')
    search_fields = ('name',)

    class Media:
        js = ('js/admin/main.js', 'js/admin/device.js',)
        css = {
            'all': ('css/admin/device.css',)
        }

    def has_module_permission(self, request):
        return False

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('specialty', 'parent').prefetch_related('sub_categories')

    def category_name(self, obj):
        if obj.sub_categories.exists():
            categories_url = reverse('admin:device_category_changelist')
            list_link = f"""
            <a href='{categories_url}?specialty__id={obj.specialty.id}&parent__id={obj.id}'>{obj.name}</a>
            """
        else:
            products_url = reverse('admin:device_product_changelist')
            list_link = f"<a href='{products_url}?category__id={obj.id}'>{obj.name}</a>"

        category_url = reverse('admin:device_category_change', args=(obj.id,))
        return format_html(f"""
            {list_link}
            &nbsp;&nbsp;
            <a href='{category_url}'><img src='/static/admin/img/icon-changelink.svg' alt='Edit'></a>
        """)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        children_ids = form.cleaned_data.get('sub_categories')
        if children_ids is not None:
            obj.sub_categories.set(Category.objects.filter(id__in=children_ids))


class ClientPricesInline(admin.StackedInline):
    model = ClientPrice
    fields = ('client', 'unit_cost', 'system_cost', 'discounts', 'inventory')
    readonly_fields = ('discounts', 'inventory')
    extra = 0

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('client', 'product').prefetch_related(
            Prefetch('discount_set', queryset=Discount.objects.order_by('apply_type', 'order'), to_attr='all_discounts')
        )

    def inventory(self, client_price):
        try:
            device = Device.objects.get(product=client_price.product, client=client_price.client)
            data = {
                'device': {
                    'id': device.id,
                    'hospital_number': device.hospital_number,
                    'bulk': 0,
                    'used_bulk': 0,
                    'consignment': 0,
                    'used_consignment': 0,
                },
                'BULK_PURCHASE': BULK_PURCHASE,
                'CONSIGNMENT_PURCHASE': CONSIGNMENT_PURCHASE,
            }
            for used, purchase_type in device.item_set.values_list('is_used', 'purchase_type').all():
                used = 'used_' if used else ''
                purchase_type = 'bulk' if purchase_type == BULK_PURCHASE else 'consignment'
                key = f'{used}{purchase_type}'
                data['device'][key] += 1

            return render_to_string('admin/hospital/device/items.html', data)
        except ObjectDoesNotExist:
            return 'N/A'

    def discounts(self, client_price):
        unit_cost_discounts = []
        system_cost_discounts = []
        for discount in client_price.all_discounts:
            if discount.cost_type == UNIT_COST:
                unit_cost_discounts.append(discount)
            else:
                system_cost_discounts.append(discount)

        today = datetime.utcnow().date()
        unit_cost_item = Item(purchased_date=today, rep_case=RepCase(procedure_date=today), cost_type=UNIT_COST)
        system_cost_item = Item(purchased_date=today, rep_case=RepCase(procedure_date=today), cost_type=SYSTEM_COST)
        return render_to_string('admin/price/client_price/link.html', {'client_price': {
            'id': client_price.id,
            'unit_cost': client_price.redeem(unit_cost_discounts, unit_cost_item),
            'system_cost': client_price.redeem(system_cost_discounts, system_cost_item),
        }})


class FeaturesInline(admin.TabularInline):
    model = Feature
    fields = ('name', 'value', 'icon', 'shared_image')
    readonly_fields = ('icon',)

    formfield_overrides = {
        models.ForeignKey: {'widget': apply_select2(forms.Select)}
    }

    def get_extra(self, request, product=None, **kwargs):
        if product:
            return product.missing_category_features.count()
        return 0

    def get_formset(self, request, product=None, **kwargs):
        initial = []
        if request.method == 'GET' and product:
            for category_feature in product.missing_category_features:
                initial.append({'shared_image': category_feature.shared_image,
                                'name': category_feature.name,
                                })

        formset = super().get_formset(request, product, **kwargs)
        formset.__init__ = curry(formset.__init__, initial=initial)
        return formset

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('category_feature', 'shared_image',
                                                            'category_feature__shared_image')

    def icon(self, feature):
        return feature.icon


class ProductAdmin(ImportExportModelAdmin):
    resource = ProductResource
    form = ProductForm
    list_display = ('name', 'model_number', 'level', 'image')
    list_filter = ('category__specialty', 'clientprice__client')
    search_fields = ('name', 'model_number')

    inlines = (ClientPricesInline, FeaturesInline)

    class Media:
        js = ('js/admin/main.js', 'js/admin/device.js',)
        css = {
            'all': ('css/admin/device.css',)
        }

    def response_change(self, request, obj):
        obj.remove_invalid_category_features()
        return super().response_change(request, obj)


class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ('name', 'image')
    search_fields = ('name',)


admin.site.register(Specialty, SpecialtyAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Manufacturer, ManufacturerAdmin)
