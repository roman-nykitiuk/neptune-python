from django.contrib import admin

from neptune.models import SharedImage


class AutoCompleteSearchAdminMixin(object):
    class Media:
        css = {
            'all': ('vendor/jquery/jquery-ui.min.css',),
        }
        js = ('js/admin/required-jquery.js',
              'vendor/jquery/jquery-ui.min.js',
              'js/admin/autocomplete-search.js',)


class SharedImageAdmin(admin.ModelAdmin):
    list_display = ('name', 'image')


admin.site.register(SharedImage, SharedImageAdmin)
