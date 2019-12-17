from django.contrib.sessions.backends.db import SessionStore
from django.urls import reverse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.auth import SESSION_KEY, BACKEND_SESSION_KEY, HASH_SESSION_KEY
from django.conf import settings

import time

from selenium.webdriver.support.select import Select

from account.factories import UserFactory

MAX_WAIT_SECONDS = 10


def wait(wait_time=MAX_WAIT_SECONDS):
    def wrapper(fn):
        def modified_fn(*args, **kwargs):
            start_time = time.time()
            while True:
                try:
                    return fn(*args, **kwargs)
                except (WebDriverException, AssertionError) as ex:
                    if time.time() - start_time > wait_time:
                        raise ex
                time.sleep(0.5)
        return modified_fn
    return wrapper


class FunctionalTestCase(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        for _ in range(3):
            try:
                chrome_options = Options()
                chrome_options.add_argument('--no-sandbox')
                chrome_options.add_argument('--disable-dev-shm-usage')
                cls.browser = webdriver.Chrome(chrome_options=chrome_options)
                break
            except Exception:
                time.sleep(1)
        super(FunctionalTestCase, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()
        super(FunctionalTestCase, cls).tearDownClass()

    def visit(self, path):
        self.browser.get(f'{self.live_server_url}/{path}')

    def visit_reverse(self, name, *args, **kwargs):
        self.browser.get(f'{self.live_server_url}{reverse(name, args=args, kwargs=kwargs)}')

    @wait()
    def wait_for(self, fn):
        fn()

    @wait()
    def wait_for_element_contains_text(self, selector, text):
        self.assertTrue(text in self.browser.find_element_by_css_selector(selector).text)

    def find_element(self, selector, parent=None):
        parent = parent or self.browser
        return parent.find_element_by_css_selector(selector)

    def find_elements(self, selector, parent=None):
        parent = parent or self.browser
        return parent.find_elements_by_css_selector(selector)

    def find_link(self, text, parent=None):
        parent = parent or self.browser
        return parent.find_element_by_link_text(text)

    def fill_form_field_with_text(self, field_name, text):
        form_field_element = self.find_element(f'[name={field_name}]')
        form_field_element.clear()
        form_field_element.send_keys(text)

    def select_option(self, selector, option_text):
        options = self.browser.find_elements_by_css_selector(f'{selector} option')
        for option in options:
            if option.text == option_text:
                option.click()
                return

    def click_submit_button(self):
        self.browser.execute_script("document.querySelector('input[type=submit]').click();")

    def click_save_and_continue(self):
        self.browser.execute_script("document.querySelector('input[name=_continue]').click();")

    def assert_option_is_selected(self, selector, option_text):
        select = Select(self.find_element(selector))
        selected_option = select.first_selected_option
        self.assertEqual(selected_option.text, option_text)

    def assert_options_are_selected(self, selector, options):
        select = Select(self.find_element(selector))
        selected_options = select.all_selected_options
        for selected_option in selected_options:
            self.assertTrue(selected_option.text in options)

    def assert_element_attribute_value(self, selector, value, attr='value'):
        self.assertEqual(self.find_element(selector).get_attribute(attr), value)

    def assert_element_to_disappear(self, selector):
        self.assertRaises(WebDriverException, self.find_element, selector)

    def assert_elements_count(self, selector, count):
        self.assertEqual(len(self.browser.find_elements_by_css_selector(selector)), count)


class MasterAdminTestCase(FunctionalTestCase):
    def setUp(self):
        super(MasterAdminTestCase, self).setUp()
        self.master_admin = UserFactory(email='admin@neptune.com', is_superuser=True, is_staff=True)
        self.master_admin.set_password('neptune123')
        self.master_admin.save()

    def log_in_master_admin(self):
        master_admin_session = SessionStore()
        master_admin_session[SESSION_KEY] = self.master_admin.pk
        master_admin_session[BACKEND_SESSION_KEY] = settings.AUTHENTICATION_BACKENDS[0]
        master_admin_session[HASH_SESSION_KEY] = self.master_admin.get_session_auth_hash()
        master_admin_session.save()

        self.visit('')
        self.browser.add_cookie({
            'name': settings.SESSION_COOKIE_NAME,
            'value': master_admin_session.session_key,
            'path': '/'
        })

    def wait_for_success_message(self, message):
        self.wait_for_element_contains_text('.messagelist .success', message)

    def wait_for_error_message(self, message=None):
        self.wait_for_element_contains_text('.errornote', message or 'Please correct the errors below.')
