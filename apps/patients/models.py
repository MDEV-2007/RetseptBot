from django.db import models


class Patient(models.Model):
    GENDER_CHOICES = [('M', 'Male'), ('F', 'Female')]

    full_name = models.CharField(max_length=255)
    age = models.PositiveIntegerField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    phone_number = models.CharField(max_length=20, blank=True)
    telegram_id = models.BigIntegerField(null=True, blank=True, help_text='Telegram chat ID (numeric)')
    telegram_username = models.CharField(max_length=100, blank=True, help_text='Telegram username (@username)')
    address = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.full_name

    def get_gender_display_icon(self):
        icons = {'M': 'M', 'F': 'F'}
        return icons.get(self.gender, '')
