from django import forms
from django.contrib import admin
from django.http import HttpResponse
from django.utils.functional import curry
from django.utils.safestring import mark_safe

from easy_select2 import apply_select2
from fsm_admin.mixins import FSMTransitionMixin

from neptune.models import SharedImage
from price.constants import UNIT_COST, SYSTEM_COST, DISCOUNTS, PERCENT_DISCOUNT, VALUE_DISCOUNT, POST_DOCTOR_ORDER, \
    DISCOUNT_APPLY_TYPES, COMPLETE_REBATE
from price.models import ClientPrice, Discount, Rebate, Tier, RebatableItem, ELIGIBLE_ITEM, REBATED_ITEM
from price.constants import NEW_REBATE


class DiscountForm(forms.ModelForm):
    cost_type = None
    percent = forms.DecimalField(max_value=100, min_value=0, required=False)
    value = forms.DecimalField(min_value=0, required=False)
    order = forms.IntegerField(min_value=1)
    apply_type = forms.ChoiceField(choices=DISCOUNT_APPLY_TYPES[0:2])

    class Meta:
        model = Discount
        fields = ('name', 'order', 'discount_type', 'percent', 'value', 'cost_type')

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('discount_type') == PERCENT_DISCOUNT and cleaned_data.get('percent') is None:
            self._errors['percent'] = self.error_class(['This field is required.'])
        if cleaned_data.get('discount_type') == VALUE_DISCOUNT and cleaned_data.get('value') is None:
            self._errors['value'] = self.error_class(['This field is required.'])
        return cleaned_data


class UnitCostDiscountForm(DiscountForm):
    cost_type = forms.CharField(widget=forms.HiddenInput(), empty_value=UNIT_COST)


class SystemCostDiscountForm(DiscountForm):
    cost_type = forms.CharField(widget=forms.HiddenInput(), empty_value=SYSTEM_COST)


class DiscountsInline(admin.TabularInline):
    model = Discount
    cost_type = UNIT_COST
    verbose_name_plural = 'Discounts on unit cost'
    fields = ('apply_type', 'name', 'discount_type', 'percent', 'value', 'order',
              'icon', 'shared_image', 'cost_type', 'start_date', 'end_date',)
    readonly_fields = ('icon',)

    class Media:
        js = []

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.filter(cost_type=self.cost_type)\
            .exclude(apply_type=POST_DOCTOR_ORDER).order_by('apply_type', 'order')

    def get_extra(self, request, obj=None, **kwargs):
        required_discounts_count = len(DISCOUNTS)
        required_discounts = DISCOUNTS.keys()
        existing_required_discounts_count = obj.discounts(self.cost_type).filter(name__in=required_discounts).count()
        extra = required_discounts_count - existing_required_discounts_count
        return extra if extra > 0 else 0

    def get_formset(self, request, obj=None, **kwargs):
        required_discounts = DISCOUNTS.keys()
        existing_required_discounts = obj.discounts(self.cost_type).filter(name__in=required_discounts) \
                                         .values_list('name', flat=True) if obj else []
        new_discounts = [discount for discount in required_discounts if discount not in existing_required_discounts]
        initial = []
        if request.method == 'GET':
            for discount in new_discounts:
                shared_image = SharedImage.objects.filter(image=f'shared/{discount}.png').first()
                initial.append({'name': discount, 'percent': 0, 'cost_type': self.cost_type, 'order': 1,
                                'apply_type': DISCOUNTS.get(discount, POST_DOCTOR_ORDER),
                                'shared_image': shared_image and shared_image.id,
                                })

        formset = super().get_formset(request, obj, **kwargs)
        formset.__init__ = curry(formset.__init__, initial=initial)
        return formset

    def icon(self, discount):
        return mark_safe(f'<img src="{discount.shared_image.image.url}" />')


class UnitCostDiscountsInline(DiscountsInline):
    form = UnitCostDiscountForm
    verbose_name_plural = 'Discounts on unit cost'
    cost_type = UNIT_COST


class SystemCostDiscountsInline(DiscountsInline):
    form = SystemCostDiscountForm
    verbose_name_plural = 'Discounts on system cost'
    cost_type = SYSTEM_COST


class ClientPriceAdmin(admin.ModelAdmin):
    model = ClientPrice
    readonly_fields = ('product', 'client')
    inlines = (UnitCostDiscountsInline, SystemCostDiscountsInline,)

    class Media:
        js = ('js/admin/main.js',
              'js/admin/price.js',)
        css = {
            'all': ('css/admin/price.css',)
        }

    def response_change(self, request, obj):
        return HttpResponse(f'''
        <script type="text/javascript">
            window.close();
            opener.location.href = opener.location.pathname + '?client-price=' + { obj.id };
        </script>
        ''')

    def has_module_permission(self, request):
        return False

    def get_inline_instances(self, request, obj=None):
        instances = super().get_inline_instances(request, obj)
        inline = request.GET.get('inline', 'unit_cost')
        inline_class_name = f"{inline.title().replace('_', '')}DiscountsInline"
        instances = [instance for instance in instances if inline_class_name == instance.__class__.__name__]
        return instances

    def get_fields(self, request, obj=None):
        inline_field = request.GET.get('inline', 'unit_cost')
        return ('product', 'client', inline_field)


class RebateForm(forms.ModelForm):
    class Meta:
        model = Rebate
        fields = ('name', 'manufacturer', 'client', 'start_date', 'end_date')
        widgets = {
            'eligible_items': apply_select2(forms.SelectMultiple),
            'rebated_items': apply_select2(forms.SelectMultiple),
            'client': apply_select2(forms.Select),
            'manufacturer': apply_select2(forms.Select),
        }


class TiersInline(admin.TabularInline):
    model = Tier
    extra = 0

    fields = ('tier_type', 'lower_bound', 'upper_bound', 'order', 'discount_type', 'percent', 'value',)

    def get_readonly_fields(self, request, rebate=None):
        if rebate and rebate.status == COMPLETE_REBATE:
            return ('tier_type', 'lower_bound', 'upper_bound', 'order', 'discount_type', 'percent', 'value',)
        return ()

    def has_delete_permission(self, request, rebate=None):
        if rebate:
            return rebate.status == NEW_REBATE
        return True


class RebatableItemForm(forms.ModelForm):
    object_id = forms.IntegerField(required=True)
    item_type = None

    class Meta:
        model = RebatableItem
        fields = ('content_type', 'object_id', 'item_type')
        widgets = {
            'content_type': apply_select2(forms.Select)
        }


class EligibleItemForm(RebatableItemForm):
    item_type = forms.IntegerField(widget=forms.HiddenInput(), initial=ELIGIBLE_ITEM)


class RebatedItemForm(RebatableItemForm):
    item_type = forms.IntegerField(widget=forms.HiddenInput(), initial=REBATED_ITEM)


class EligibleItemsInline(admin.TabularInline):
    model = RebatableItem
    form = EligibleItemForm
    extra = 0
    verbose_name_plural = 'Eligible Items'

    def get_queryset(self, request):
        return super().get_queryset(request).filter(item_type=ELIGIBLE_ITEM)


class RebatedItemsInline(admin.TabularInline):
    model = RebatableItem
    form = RebatedItemForm
    extra = 0
    verbose_name_plural = 'Rebated Items'

    def get_queryset(self, request):
        return super().get_queryset(request).filter(item_type=REBATED_ITEM)


class RebateAdmin(FSMTransitionMixin, admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'status')
    form = RebateForm
    fields = ('name', 'manufacturer', 'client', 'start_date', 'end_date', 'status')
    fsm_field = ('status',)
    readonly_fields = ('status',)
    inlines = (TiersInline, RebatedItemsInline, EligibleItemsInline)

    class Media:
        js = ('js/admin/main.js',
              'js/admin/price.js',)
        css = {
            'all': ('css/admin/price.css',)
        }

    def get_inline_instances(self, request, obj=None):
        instances = super().get_inline_instances(request, obj)
        if obj is None:
            instances = [instance for instance in instances if isinstance(instance, TiersInline)]
        return instances


admin.site.register(ClientPrice, ClientPriceAdmin)
admin.site.register(Rebate, RebateAdmin)
