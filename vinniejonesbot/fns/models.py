from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class FnsUser(models.Model):
    phone = PhoneNumberField(region='RU', null=True, blank=True)
    password = models.CharField(max_length=16, null=True, blank=True)
