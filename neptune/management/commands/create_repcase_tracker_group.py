from django.contrib.auth.models import Group, Permission
from django.core.management import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        repcase_tracker_group, created = Group.objects.get_or_create(name='Repcase Tracker')
        if created:
            print('New group created')
        else:
            print('Group exists')

        tracker_repcase_permissions = Permission.objects.filter(content_type__app_label='tracker',
                                                                content_type__model='repcase').all()
        hospital_item_permissions = Permission.objects.filter(content_type__app_label='hospital',
                                                              content_type__model='item').all()
        repcase_tracker_group.permissions.add(*tracker_repcase_permissions)
        repcase_tracker_group.permissions.add(*hospital_item_permissions)

        print('Group permissions:')
        for permission in repcase_tracker_group.permissions.all():
            print(f'+ {permission.name}')
