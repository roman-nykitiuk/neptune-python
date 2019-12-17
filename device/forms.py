from urllib.parse import parse_qs

from django import forms
from django.core.exceptions import ValidationError

from easy_select2 import apply_select2
from easy_select2.forms import FixedModelForm

from device.models import Category, Specialty


def get_changelist_filters(view_kwargs):
    changelist_filters_query_string = view_kwargs.get('initial', {}).get('_changelist_filters', '')
    return parse_qs(changelist_filters_query_string)


class CategoryForm(FixedModelForm):
    sub_categories = forms.MultipleChoiceField(widget=apply_select2(forms.SelectMultiple), required=False)

    class Meta:
        fields = ('name', 'specialty', 'image', 'sub_categories', 'parent')
        model = Category
        widgets = {
            'parent': apply_select2(forms.Select),
            'specialty': apply_select2(forms.Select),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        changelist_filters = get_changelist_filters(kwargs)

        current_choices = list(self.instance.sub_categories.values_list('id', 'name'))
        other_choices = list(Category.objects.filter(parent=None)
                             .exclude(id=self.instance.id)
                             .values_list('id', 'name'))
        self.fields['sub_categories'].choices = current_choices + other_choices
        self.fields['sub_categories'].widget.template_name = 'admin/device/category/sub_categories.html'
        self.initial['sub_categories'] = list(self.instance.sub_categories.values_list('id', flat=True))
        if not self.instance.id:
            self.initial['specialty'] = changelist_filters.get('specialty__id', [0])[0]
            self.initial['parent'] = changelist_filters.get('parent__id', [0])[0]

    def clean(self):
        cleaned_data = self.cleaned_data
        parent_category = cleaned_data.get('parent')
        if parent_category:
            new_sub_categories = Category.objects.filter(id__in=cleaned_data['sub_categories'])
            new_grandparent_categories = Category.get_all_parent_categories([parent_category.id])
            new_parent_category_ids = ([parent_category.id] +
                                       list(new_grandparent_categories.values_list('id', flat=True)))
            if new_sub_categories.filter(id__in=new_parent_category_ids).exists():
                raise ValidationError('Circular sub categories assigned.')

        return cleaned_data


class ProductForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        specialties = Specialty.objects.all().prefetch_related('category_set')
        choices = []
        for specialty in specialties:
            categories = [(category.id, category.name) for category in specialty.category_set.all()]
            choices.append((specialty.name, categories))
        self.fields['category'].choices = choices
        if not self.instance.id:
            self.initial['category'] = get_changelist_filters(kwargs).get('category__id', [0])[0]

    class Meta:
        widgets = {
            'category': apply_select2(forms.Select),
            'manufacturer': apply_select2(forms.Select),
            'level': apply_select2(forms.Select),
        }
