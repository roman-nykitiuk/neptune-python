from django.contrib import admin, auth
from django.contrib.auth.models import Group
from django.template.loader import render_to_string
from knox.models import AuthToken
from import_export.admin import ImportExportActionModelAdmin

from account.models import User
from account.resources import UserResource
from hospital.admin import AccountForm
from hospital.models import Account
from neptune.admin import AutoCompleteSearchAdminMixin


class AccountsInline(admin.TabularInline):
    model = Account
    form = AccountForm
    fields = ('role', 'client')
    extra = 0


class UserAdmin(auth.admin.UserAdmin, AutoCompleteSearchAdminMixin, ImportExportActionModelAdmin):
    list_display = ('email', 'name', 'accounts')
    readonly_fields = ('date_joined', 'last_login', 'accounts')
    fieldsets = (
        (None, {'fields': ('name', 'email', 'password')}),
        ('Permission', {'fields': ('is_staff', 'groups',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('name', 'email', 'password1', 'password2'),
        }),
    )
    ordering = ('email',)
    search_fields = ('email', 'name', 'clients__name')
    list_filter = ('account__role', 'account__client')

    inlines = (AccountsInline,)

    resource_class = UserResource

    class Media(AutoCompleteSearchAdminMixin.Media):
        css = {
            'all': AutoCompleteSearchAdminMixin.Media.css['all'] + ('css/admin/account.css',)
        }

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('account_set__role', 'account_set__client',
                                                              'account_set__specialties')

    def accounts(self, user):
        accounts = user.account_set.all()
        return render_to_string('admin/account/user/accounts.html', {'accounts': accounts})
    accounts.short_description = 'Works as'


admin.site.unregister(Group)
admin.site.unregister(AuthToken)

admin.site.register(User, UserAdmin)
