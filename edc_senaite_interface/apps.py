from django.conf import settings
from django.apps import AppConfig as DjangoAppConfig
from edc_device.apps import AppConfig as BaseEdcDeviceAppConfig

from edc_device.constants import CENTRAL_SERVER


class AppConfig(DjangoAppConfig):

    name = 'edc_senaite_interface'
    verbose_name = 'EDC SENAITE INTERFACE'
    admin_site_name = 'edc_senaite_interface_admin'
    client = None
    host = None
    courier = None
    sample_type_match = None
    container_type_match = None
    template_match = None
    DEVICE_ID = '99'
    DEVICE_ROLE = CENTRAL_SERVER

    def ready(self):
        from .signals import senaite_sample_create_on_post_save


class EdcDeviceAppConfig(BaseEdcDeviceAppConfig):
    use_settings = True
    device_id = settings.DEVICE_ID
    device_role = settings.DEVICE_ROLE

