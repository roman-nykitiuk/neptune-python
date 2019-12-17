from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django import forms
from easy_select2 import apply_select2

from hospital.constants import BULK_PURCHASE, CONSIGNMENT_PURCHASE
from hospital.models import Account, Item
from price.constants import PRE_DOCTOR_ORDER
from price.models import Discount
from tracker.models import RepCase


class RepCaseForm(forms.ModelForm):
    owners = forms.ModelMultipleChoiceField(
        widget=apply_select2(forms.SelectMultiple),
        queryset=Account.objects.all().prefetch_related('role', 'user')
    )
    physician = forms.ModelChoiceField(
        widget=apply_select2(forms.Select),
        queryset=Account.objects.all().prefetch_related('role', 'user')
    )

    class Meta:
        model = RepCase
        fields = ('client', 'owners', 'procedure_date', 'status')
        widgets = {
            'client': apply_select2(forms.Select),
            'client_id': forms.HiddenInput()
        }

    def clean(self):
        data = self.cleaned_data
        client = data.get('client')
        if client:
            owners = data.get('owners', [])
            for owner in owners:
                try:
                    client.account_set.get(pk=owner.pk)
                except ObjectDoesNotExist:
                    raise ValidationError(f'Invalid {owner} for {client}')


class IdentifierSelect(forms.TextInput):
    template_name = 'admin/hospital/item/select.html'

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['BULK_PURCHASE'] = BULK_PURCHASE
        context['CONSIGNMENT_PURCHASE'] = CONSIGNMENT_PURCHASE
        context['form_field_prefix'] = name.replace('identifier', '')
        context['item'] = self.item
        return context


class RepCaseItemForm(forms.ModelForm):
    discounts = forms.ModelMultipleChoiceField(queryset=Discount.objects.all(), required=False)
    identifier = forms.CharField(widget=IdentifierSelect(), required=True)

    class Meta:
        model = Item
        fields = ('purchase_type', 'device', 'identifier', 'not_implanted_reason', 'cost_type', 'discounts')

        widgets = {
            'purchase_type': forms.HiddenInput(),
            'device': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['identifier'].widget.item = self.instance

    def clean(self):
        if not self.cleaned_data['id'] and self.cleaned_data['purchase_type'] == CONSIGNMENT_PURCHASE:
            try:
                identifier = self.cleaned_data.get('identifier')
                Item.objects.get(identifier=identifier)
                self.add_error('identifier', ValidationError(f'Item with this identifier {identifier} exists'))
            except ObjectDoesNotExist:
                pass

        return self.cleaned_data

    def save(self, commit=True):
        if not self.instance.id:
            if self.instance.purchase_type == BULK_PURCHASE:
                item = Item.objects.get(identifier=self.cleaned_data.get('identifier'))
                discount_ids = list(self.cleaned_data['discounts'].values_list('id', flat=True)) + \
                    list(item.discounts.filter(apply_type=PRE_DOCTOR_ORDER).values_list('id', flat=True))
                self.cleaned_data['discounts'] = Discount.objects.filter(id__in=discount_ids).all()
                item.rep_case = self.cleaned_data['rep_case']
            else:
                item = self.instance
                item.serial_number = item.identifier

            item.not_implanted_reason = self.instance.not_implanted_reason
            item.is_used = True
            self.instance = item

        self.instance.update_cost(self.cleaned_data['discounts'])
        return super().save(commit)
