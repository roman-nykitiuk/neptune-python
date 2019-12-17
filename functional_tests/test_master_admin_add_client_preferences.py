from django.contrib.contenttypes.models import ContentType

from device.factories import SpecialtyFactory, CategoryFactory
from functional_tests.base import MasterAdminTestCase
from hospital.factories import ClientFactory
from order.factories import PreferenceFactory, QuestionFactory


class ClientPreferenceAdminTestCase(MasterAdminTestCase):
    def setUp(self):
        super().setUp()
        self.log_in_master_admin()
        self.client = ClientFactory(name='EA')
        specialty_1 = SpecialtyFactory(name='Structure Heart')
        specialty_2 = SpecialtyFactory(name='Orthopedic')
        CategoryFactory(name='DDD Pacemakers', specialty=specialty_1)
        CategoryFactory(name='VVI ICD', specialty=specialty_2)
        QuestionFactory(name='Longevity')
        QuestionFactory(name='Remote support')
        self.visit_reverse('admin:order_preference_add')
        self.wait_for_element_contains_text('.model-preference.change-form', 'Add preference')

    def test_add_new_preference_to_client(self):
        self.wait_for_element_contains_text('.form-row.field-object_id', 'Specialty: Structure Heart')
        self.wait_for_element_contains_text('.form-row.field-object_id', 'Specialty: Orthopedic')
        self.wait_for_element_contains_text('.form-row.field-object_id', 'Category: DDD Pacemakers')
        self.wait_for_element_contains_text('.form-row.field-object_id', 'Category: VVI ICD')

        self.select_option('#id_object_id', 'Category: DDD Pacemakers')
        self.select_option('#id_client', self.client.name)
        for index in range(2):
            self.find_link('Add another Question').click()
            self.select_option(f'#id_questionnaire_set-{index}-question', 'Longevity')
        self.click_save_and_continue()
        self.wait_for_error_message(message='Please correct the errors below.')
        self.wait_for_element_contains_text('fieldset ul.errorlist', 'Please correct the duplicate data for question.')
        self.wait_for_element_contains_text('tbody ul.errorlist', 'Please correct the duplicate values below.')

        self.select_option(f'#id_questionnaire_set-0-question', 'Remote support')
        self.click_save_and_continue()
        self.wait_for_success_message('The preference "Default" was added successfully.')
        self.assert_option_is_selected('#id_client', self.client.name)
        self.assert_option_is_selected('#id_object_id', 'Category: DDD Pacemakers')
        self.assert_elements_count('tr.form-row.has_original td.field-question', count=2)
        self.assert_option_is_selected('#id_questionnaire_set-1-question', 'Longevity')
        self.assert_option_is_selected('#id_questionnaire_set-0-question', 'Remote support')

    def test_add_duplicate_preference(self):
        self.click_save_and_continue()
        self.wait_for_success_message('The preference "Default" was added successfully.')

        self.visit_reverse('admin:order_preference_add')
        self.wait_for_element_contains_text('.model-preference.change-form', 'Add preference')
        self.click_save_and_continue()
        self.wait_for_error_message(message='Please correct the error below.')
        self.wait_for_element_contains_text('.errorlist.nonfield', 'Preference for client, specialty/category exists')


class PreferenceAdminTestCase(MasterAdminTestCase):
    def setUp(self):
        super().setUp()
        client = ClientFactory(name='UVMC')
        specialty = SpecialtyFactory(name='CDM')
        category = CategoryFactory(name='Pacemaker', specialty=specialty)
        PreferenceFactory(name='Default for all products',
                          client=None, content_type=None, object_id=None,
                          questions=[QuestionFactory(name='Longevity')])
        PreferenceFactory(name='Preferences for client',
                          client=client, content_type=None, object_id=None,
                          questions=[QuestionFactory(name='Size/shape')])
        PreferenceFactory(name='Preferences for client:specialty',
                          client=client, object_id=specialty.id,
                          content_type=ContentType.objects.get(app_label='device', model='specialty'),
                          questions=[QuestionFactory(name='Research')])
        PreferenceFactory(name='Preferences for client:category',
                          client=client, object_id=category.id,
                          content_type=ContentType.objects.get(app_label='device', model='category'),
                          questions=[QuestionFactory(name='cost')])
        self.log_in_master_admin()
        self.visit_reverse('admin:order_preference_changelist')
        self.wait_for_element_contains_text('.model-preference #content h1', 'Select preference to change')

    def test_preferences_listing_sorted_by_client_and_content_type(self):
        self.wait_for_element_contains_text('p.paginator', '4 preferences')
        rows = self.find_elements('#result_list tbody tr')
        self.assertEquals(rows[0].text, 'Preferences for client:category UVMC category Pacemaker')
        self.assertEquals(rows[1].text, 'Preferences for client:specialty UVMC specialty CDM')
        self.assertEquals(rows[2].text, 'Preferences for client UVMC - -')
        self.assertEquals(rows[3].text, 'Default for all products - - -')
