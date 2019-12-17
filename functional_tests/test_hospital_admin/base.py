import json
import os

from django.conf import settings

from account.factories import UserFactory
from functional_tests.base import FunctionalTestCase
from hospital.constants import RolePriority
from hospital.factories import ClientFactory, AccountFactory, RoleFactory


class HospitalAdminTestCase(FunctionalTestCase):
    def setUp(self):
        super().setUp()
        self.client = ClientFactory(name='Central Dental Hospital')
        self.physician = AccountFactory(user=UserFactory(email='physician@neptune.com'), client=self.client).user
        self.admin = AccountFactory(user=UserFactory(email='admin@neptune.com'), client=self.client,
                                    role=RoleFactory(priority=RolePriority.ADMIN.value)).user

    @classmethod
    def tearDownClass(cls):
        cls.collect_js_coverage()
        super().tearDownClass()

    @classmethod
    def collect_js_coverage(cls):
        js_coverage = cls.browser.execute_script('return window.__coverage__;')
        coverage_json_name = f'coverage-{cls.__module__}.{cls.__name__}.json'
        coverage_json_path = os.path.join(settings.BASE_DIR, '.nyc_output', coverage_json_name)
        with open(coverage_json_path, 'w') as file:
            json.dump(js_coverage, file)
