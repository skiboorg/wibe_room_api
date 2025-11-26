import datetime
import uuid

from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db.models.signals import post_save, pre_delete
from django.utils import timezone
from datetime import timedelta
# from .tasks import send_email

import logging
logger = logging.getLogger(__name__)

class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(email, password, **extra_fields)




class User(AbstractUser):
    username = None
    firstname = None
    lastname = None
    avatar = models.FileField(upload_to='avatars', null=True, blank=True)
    email = models.EmailField('Почта', max_length=255, blank=True, null=True, unique=True)
    tg_username = models.CharField('Телега юзер', max_length=255, blank=True, null=True)
    tg_id = models.CharField('Телега ID', max_length=255, blank=True, null=True)
    full_name = models.CharField('ФИО', max_length=255, blank=True, null=True)
    phone = models.CharField('Телефон', max_length=255, blank=True, null=True, unique=True)
    comment = models.TextField('Коментарий', blank=True, null=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = UserManager()

    def __str__(self):
        return f'{self.full_name}'

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = '1. Пользователи'


def user_post_save(sender, instance, created, **kwargs):
    #import monthdelta
    #datetime.date.today() + monthdelta.monthdelta(months=1)

    if created:
        print('created')


post_save.connect(user_post_save, sender=User)

