from django.conf import settings

from .senaite_user import SenaiteUser

if 'edc_senaite_interface' in settings.APP_NAME:
    from ..tests.models import *
