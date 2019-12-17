from django.contrib import admin
from django.utils.safestring import mark_safe
from import_export.admin import ImportExportActionModelAdmin

from hospital.models import Item
from tracker.forms import RepCaseForm, RepCaseItemForm
from tracker.models import RepCase, PurchasePrice
from tracker.resources import PurchasePriceResource


class ItemsInline(admin.TabularInline):
    model = Item
    form = RepCaseItemForm
    extra = 0

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('device__product',
                                                            'device__product__category',
                                                            'device__product__category__specialty',
                                                            'device__product__manufacturer')

    def has_delete_permission(self, request, obj=None):
        return False


class RepCaseAdmin(admin.ModelAdmin):
    form = RepCaseForm
    fields = ('client', 'owners', 'physician', 'procedure_date', 'status', 'client_id')
    list_display = ('client', 'physician', 'procedure_date')
    inlines = (ItemsInline,)

    def client_id(self, rep_case):
        return mark_safe(f'<input id="repcase-client-id" type="hidden" value={rep_case.client_id} />')

    def get_readonly_fields(self, request, obj=None):
        return ('client', 'client_id') if obj else ('client_id',)

    def get_inline_instances(self, request, obj=None):
        if obj:
            return super().get_inline_instances(request, obj)
        return []

    class Media:
        css = {
            'all': ('css/admin/tracker.css',)
        }
        js = ('js/admin/main.js', 'js/admin/tracker.js',)


class PurchasePriceAdmin(ImportExportActionModelAdmin):
    resource_class = PurchasePriceResource
    list_display = ('avg', 'year', 'client', 'category', 'level', 'cost_type')


admin.site.register(RepCase, RepCaseAdmin)
admin.site.register(PurchasePrice, PurchasePriceAdmin)
