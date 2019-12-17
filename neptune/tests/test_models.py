from django.test import TestCase

from neptune.factories import SharedImageFactory


class SharedImageTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.shared_image = SharedImageFactory(name='url',)

    def test_to_string(self):
        self.assertEqual(str(self.shared_image), 'url')
