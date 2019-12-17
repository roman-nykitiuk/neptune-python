from django.conf import settings
from django.test import TestCase, override_settings
from factory.django import ImageField
from shutil import rmtree

from neptune.factories import SharedImageFactory
from neptune.utils import make_imagefield_filepath


class MakeImageFieldFilePath(TestCase):
    def setUp(self):
        self.instance = SharedImageFactory(name='url')

    def test_uploading_filepath_not_existing(self):
        uploading_filename = make_imagefield_filepath('shared', self.instance, 'test_image.png')
        self.assertEqual(uploading_filename, 'shared/test_image.png')

    @override_settings(DEFAULT_FILE_STORAGE='django.core.files.storage.FileSystemStorage')
    def test_uploading_filepath_exists(self):
        SharedImageFactory(name='shock',
                           image=ImageField(filename='test_image.png'))
        uploading_filename = make_imagefield_filepath('shared', self.instance, 'test_image.png')
        self.assertRegex(uploading_filename, r'shared\/test_image-\d+\.png')

        rmtree(settings.MEDIA_ROOT)
