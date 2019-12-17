from django.contrib import admin
from django.contrib.postgres.fields import JSONField
from prettyjson import PrettyJSONWidget

from order.forms import PreferenceForm
from order.models import Preference, Order, Question, Questionnaire


class OrderAdmin(admin.ModelAdmin):
    model = Order
    list_display = ('product', 'procedure_datetime', 'physician', 'status')
    fields = ('status', 'product', 'procedure_datetime', 'physician', 'cost_type', 'discounts')
    readonly_fields = ('product', 'procedure_datetime', 'physician', 'cost_type')
    list_filter = ['physician__client', 'product__category__specialty']
    formfield_overrides = {
        JSONField: {'widget': PrettyJSONWidget(attrs={'initial': 'parsed'})}
    }


class QuestionnairesInline(admin.TabularInline):
    model = Questionnaire
    fields = ('question', 'preference')
    extra = 0
    verbose_name = 'Question'
    verbose_name_plural = 'Questions'


class PreferenceAdmin(admin.ModelAdmin):
    model = Preference
    list_display = ('name', 'client', 'content_type', 'content_object')
    fields = ('name', 'client', 'content_type', 'object_id')
    readonly_fields = ('content_object',)
    inlines = (QuestionnairesInline,)
    form = PreferenceForm

    class Media:
        js = ('js/admin/main.js',)

    def content_object(self, preference):
        return preference.content_object
    content_object.short_description = 'Specialty/Category name'

    def get_queryset(self, request):
        return super().get_queryset(request).order_by('client', 'content_type__model', 'object_id')


class QuestionAdmin(admin.ModelAdmin):
    model = Question

    def has_module_permission(self, request):
        return False


admin.site.register(Preference, PreferenceAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Order, OrderAdmin)
