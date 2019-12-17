from datetime import datetime

from django.contrib import admin
from django import forms
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.html import format_html

from easy_select2 import apply_select2
from easy_select2.forms import FixedModelForm
from import_export.admin import ImportExportActionModelAdmin

from device.models import Specialty
from hospital.models import Client, Device, Role, Account, Item
from hospital.resources import AccountResource, ItemResource
from hospital.constants import BULK_PURCHASE
from neptune.admin import AutoCompleteSearchAdminMixin


class ClientForm(FixedModelForm):
    children = forms.MultipleChoiceField(widget=apply_select2(forms.SelectMultiple), required=False,
                                         label='Affiliate hospitals')

    class Meta:
        widgets = {
            'country': apply_select2(forms.Select),
        }

    def __init__(self, *args, **kwargs):
        super(ClientForm, self).__init__(*args, **kwargs)
        current_choices = list(self.instance.children.values_list('id', 'name'))
        other_choices = list(Client.objects.filter(parent=None)
                                           .exclude(id=self.instance.id)
                                           .exclude(id=self.instance.root_parent_id)
                                           .values_list('id', 'name'))
        self.fields['children'].choices = current_choices + other_choices
        self.fields['children'].widget.template_name = 'admin/hospital/client/children.html'
        self.initial['children'] = list(self.instance.children.values_list('id', flat=True))


class DeviceForm(forms.ModelForm):
    class Meta:
        model = Device
        fields = ('product',)
        widgets = {
            'product': apply_select2(forms.Select),
        }


class AccountForm(forms.ModelForm):
    specialties = forms.ModelMultipleChoiceField(queryset=Specialty.objects.all(),
                                                 required=False, widget=apply_select2(forms.SelectMultiple))

    class Meta:
        model = Account
        fields = ('user', 'role', 'client', 'specialties')
        widgets = {
            'user': apply_select2(forms.Select),
            'role': apply_select2(forms.Select),
            'client': apply_select2(forms.Select),
        }


class AccountAdmin(ImportExportActionModelAdmin):
    resource_class = AccountResource
    form = AccountForm
    list_display = ('user', 'role', 'client_link')
    readonly_fields = ('client_link',)
    fields = ('user', 'role', 'client')
    search_fields = ('client__name',)
    list_filter = ('client',)

    def get_queryset(self, request):
        queryset = super(AccountAdmin, self).get_queryset(request)
        return queryset.order_by('client', '-role__priority', 'user')

    def client_link(self, account):
        return render_to_string('admin/hospital/client/link.html', {'client': account.client})
    client_link.short_description = 'Client'

    def has_module_permission(self, request):
        return False


class ListAccountsInline(admin.TabularInline):
    form = AccountForm
    model = Account
    fields = ('user', 'role', 'specialties')
    readonly_fields = ('user',)
    extra = 0

    def get_queryset(self, request):
        queryset = super().get_queryset(request).select_related('user', 'role').prefetch_related('specialties')
        return queryset

    def has_add_permission(self, request):
        return False


class AddAccountsInline(admin.TabularInline):
    form = AccountForm
    model = Account
    fields = ('user', 'role', 'specialties')
    extra = 0
    verbose_name_plural = 'Add new users'

    def get_queryset(self, request):
        return super().get_queryset(request).filter(id=None)


class ClientAdmin(admin.ModelAdmin, AutoCompleteSearchAdminMixin):
    form = ClientForm
    list_display = ('name', 'street', 'city', 'state', 'country', 'parent_client')
    readonly_fields = ('specialties', 'parent_client', 'inventory')
    fields = ('name', 'street', 'city', 'state', 'country', 'image', 'notes', 'children',
              'contact_name', 'contact_phone', 'contact_email', 'specialties', 'inventory')

    inlines = (ListAccountsInline, AddAccountsInline)

    list_filter = ('device__product__category__specialty__name',)
    search_fields = ('name', 'parent__name', 'children__name', 'device__product__name', 'state', 'city',
                     'device__product__category__name', 'device__product__category__specialty__name')

    class Media(AutoCompleteSearchAdminMixin.Media):
        css = {
            'all': AutoCompleteSearchAdminMixin.Media.css['all'] + ('css/admin/hospital.css',),
        }
        js = AutoCompleteSearchAdminMixin.Media.js + (
            'js/admin/main.js',
            'js/admin/hospital.js',
        )

    def parent_client(self, client):
        return render_to_string('admin/hospital/client/link.html',
                                {'client': client.parent})

    def specialties(self, client):
        specialties = Specialty.objects.filter(category__product__clientprice__client=client).distinct()
        return render_to_string('admin/hospital/client/specialties.html',
                                {'specialties': specialties})

    def inventory(self, client):
        items_url = reverse('admin:hospital_item_changelist')
        return format_html(f"""
        <a href='{items_url}?device__client__id__exact={client.id}&is_used__exact=0&purchase_type__exact=1'>
            Manage bulk serial numbers
        </a>
        """)

    def save_model(self, request, obj, form, change):
        super(ClientAdmin, self).save_model(request, obj, form, change)
        children_ids = form.cleaned_data.get('children')
        if children_ids is not None:
            obj.set_children(children_ids)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('parent')


class RoleAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ('lot_number', 'serial_number', 'expired_date', 'purchased_date',
                  'cost', 'purchase_type')

    def clean(self):
        cleaned_data = super().clean()
        if not (cleaned_data.get('lot_number') or cleaned_data.get('serial_number')):
            raise ValidationError('Either serial number or lot number must be present.')


class ItemsInline(admin.StackedInline):
    model = Item
    form = ItemForm
    fields = ('identifier', 'serial_number', 'lot_number', 'expired_date', 'purchased_date',
              'purchase_type', 'is_used', 'discount_details')
    readonly_fields = ('identifier', 'discount_details')
    extra = 0

    def get_queryset(self, request):
        purchase_type = int(request.GET.get('purchase', BULK_PURCHASE))
        is_used = int(request.GET.get('used')) == 1
        return super().get_queryset(request).filter(purchase_type=purchase_type, is_used=is_used)

    def has_add_permission(self, request):
        return False

    def discount_details(self, item):
        return format_html(item.discounts_as_table)


class DeviceAdmin(admin.ModelAdmin):
    inlines = (ItemsInline,)
    fields = ('client', 'product', 'hospital_number', 'inventory')
    readonly_fields = ('client', 'product', 'inventory')

    class Media:
        js = ('js/admin/main.js', 'js/admin/hospital.js',)
        css = {
            'all': ('css/admin/main.css',)
        }

    def get_queryset(self, request):
        self.query_params = request.GET
        return super().get_queryset(request)

    def has_module_permission(self, request):
        return False

    def response_change(self, request, obj):
        return HttpResponse('''
            <script type="text/javascript">
                window.close();
                opener.location.reload();
            </script>
        ''')

    def inventory(self, device):
        return (
            f"{'Used in' if self.query_params.get('used') == '1' else 'Available'} "
            f"{'Bulk' if int(self.query_params.get('purchase', BULK_PURCHASE)) == BULK_PURCHASE else 'Consignment'}"
        )


class ItemAdmin(ImportExportActionModelAdmin):
    resource_class = ItemResource
    list_filter = ('is_used', 'purchase_type', 'device__product__category__specialty',
                   'device__product__manufacturer', 'device__client')
    list_select_related = ('device', 'device__client', 'device__product', 'device__product__manufacturer')
    list_display = ('identifier', 'hospital_name', 'manufacturer_name', 'hospital_number', 'model_number',
                    'serial_number', 'lot_number', 'purchased_date', 'expired_date', 'cost_type', 'is_used',
                    'item_discounts')
    fields = ('serial_number', 'lot_number', 'purchased_date', 'expired_date', 'purchase_type', 'is_used',
              'product', 'discounts_details')
    readonly_fields = ('hospital_name', 'manufacturer_name', 'hospital_number', 'model_number',
                       'product', 'discounts_details')
    search_fields = ('device__hospital_number', 'device__product__model_number', 'device__product__name')

    def hospital_name(self, item):
        return item.device.client

    def manufacturer_name(self, item):
        return item.device.product.manufacturer

    def product(self, item):
        product = item.device.product
        return format_html(f"""
        <a href="{reverse('admin:device_product_change', args=(product.id,))}">{product.name}</a>
        """)

    def hospital_number(self, item):
        device = item.device
        device_url = (f"{reverse('admin:hospital_device_change', args=(device.id,))}"
                      f"?used={int(item.is_used)}&purchase={item.purchase_type}")

        return format_html(f"<a href='{device_url}'>{item.device.hospital_number}</a>")
    hospital_number.short_description = 'Hospital part #'

    def item_discounts(self, item):
        today_purchased_date = datetime.utcnow().date()
        discounts = ''.join(f"""
        <li>
            {discount.display_name}
        </li>
        """ for discount in item.discounts.all() if discount.is_valid(today_purchased_date))

        return format_html(f"<ul>{discounts}</ul>")

    def discounts_details(self, item):
        return format_html(item.discounts_as_table)

    def model_number(self, item):
        return item.device.product.model_number
    model_number.short_description = 'Manufacturer part #'

    def has_add_permission(self, request):
        return False

    def get_queryset(self, request):
        return super().get_queryset(request).order_by('is_used').prefetch_related('discounts')


admin.site.register(Client, ClientAdmin)
admin.site.register(Account, AccountAdmin)
admin.site.register(Role, RoleAdmin)
admin.site.register(Device, DeviceAdmin)
admin.site.register(Item, ItemAdmin)
