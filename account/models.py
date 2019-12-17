from functools import partial

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from account.managers import UserManager
from neptune.utils import make_imagefield_filepath


class User(AbstractUser):
    username = None
    first_name = None
    last_name = None
    email = models.EmailField(_('email address'), unique=True)
    clients = models.ManyToManyField('hospital.Client', through='hospital.Account')
    name = models.CharField(_('name'), max_length=255, null=True, blank=False)
    default_client = models.ForeignKey('hospital.Client', on_delete=models.DO_NOTHING, null=True, blank=True,
                                       related_name='+')
    image = models.ImageField(upload_to=partial(make_imagefield_filepath, 'users'), null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()
