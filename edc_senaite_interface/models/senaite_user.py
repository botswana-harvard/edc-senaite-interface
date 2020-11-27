from django.db import models

from django_crypto_fields.fields import EncryptedCharField
from edc_base.model_mixins.base_uuid_model import BaseUuidModel


class SenaiteUser(BaseUuidModel, models.Model):

    username = models.CharField(
        verbose_name="Senaitte Username",
        null=True,
        max_length=200)

    contact = models.CharField(
        verbose_name="Contact",
        null=True,
        max_length=300)

    password = EncryptedCharField(
        verbose_name='Senaite LIMS Password',
        blank=False,
        null=True,
        help_text='Senaite LIMS password')
