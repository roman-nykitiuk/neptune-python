from django import forms
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from easy_select2 import apply_select2

from device.models import Specialty, Category
from order.models import Preference


class PreferenceForm(forms.ModelForm):
    content_type = forms.ModelChoiceField(
        queryset=ContentType.objects.filter(app_label='device', model__in=['category', 'specialty']),
        widget=forms.HiddenInput(),
        required=False
    )
    object_id = forms.ChoiceField(widget=apply_select2(forms.Select), label='Specialty/Category name')

    class Meta:
        model = Preference
        fields = ('name', 'client', 'content_type', 'object_id')
        widgets = {
            'client': apply_select2(forms.Select),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        choices = [('_0', '-------')]

        for id, name in Specialty.objects.values_list('id', 'name'):
            choices.append((f'specialty_{id}', f'Specialty: {name}'))

        for category in Category.objects.all():
            if not category.sub_categories.exists():
                choices.append((f'category_{category.id}', f'Category: {category.name}'))

        self.fields['object_id'].choices = choices
        try:
            model = ContentType.objects.get(id=self.initial.get('content_type')).model
            self.initial['object_id'] = f"{model}_{self.initial.get('object_id')}"
        except ObjectDoesNotExist:
            pass

    def clean_object_id(self):
        content_object_id = self.cleaned_data.get('object_id')
        content_type_model, cleaned_object_id = content_object_id.split('_')
        if cleaned_object_id != '0':
            self.cleaned_data['content_type'] = ContentType.objects.get(app_label='device', model=content_type_model)
            return cleaned_object_id
        else:
            return None

    def clean(self):
        preferences = Preference.objects.filter(client_id=self.cleaned_data.get('client'),
                                                content_type=self.cleaned_data.get('content_type'),
                                                object_id=self.cleaned_data.get('object_id')) \
                                        .exclude(pk=self.instance.id)
        if preferences.exists():
            raise ValidationError('Preference for client, specialty/category exists')

        return self.cleaned_data
