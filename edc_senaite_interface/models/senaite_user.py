from django.db import models

from django_crypto_fields.fields import EncryptedCharField
from edc_base.model_mixins.base_uuid_model import BaseUuidModel


class SenaiteUser(BaseUuidModel, models.Model):

    username = models.CharField(
        verbose_name="Senaite username",
        null=True,
        max_length=200)

    related_username = models.CharField(
        verbose_name='EDC related username',
        null=True,
        max_length=200)

    contact = models.CharField(
        verbose_name="Contact",
        null=True,
        max_length=300)

    password = EncryptedCharField(
        verbose_name='Senaite LIMS password',
        blank=False,
        null=True,
        help_text='Senaite LIMS password')

    def __str__(self):
        return f'username: {self.username}, contact: {self.contact}'
