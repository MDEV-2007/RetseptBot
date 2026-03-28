from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class DoctorManager(BaseUserManager):
    def create_user(self, telegram_id, full_name, password=None):
        user = self.model(telegram_id=telegram_id, full_name=full_name)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, telegram_id, full_name, password):
        user = self.create_user(telegram_id, full_name, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class Doctor(AbstractBaseUser, PermissionsMixin):
    telegram_id = models.BigIntegerField(unique=True)
    full_name = models.CharField(max_length=255)
    username = models.CharField(max_length=150, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    specialty = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'telegram_id'
    REQUIRED_FIELDS = ['full_name']

    objects = DoctorManager()

    class Meta:
        verbose_name = 'Doctor'
        verbose_name_plural = 'Doctors'

    def __str__(self):
        return self.full_name
