from django.db import models
from django.utils.translation import gettext_lazy as _

from functools import partial

from neptune.utils import make_imagefield_filepath


class SharedImage(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(_('Shared image'), upload_to=partial(make_imagefield_filepath, 'shared'))

    def __str__(self):
        return self.name
