from django.apps import AppConfig as DjangoAppConfig


class AppConfig(DjangoAppConfig):

    name = 'edc_senaite_interface'
    verbose_name = 'EDC SENAITE INTERFACE'
    admin_site_name = 'edc_senaite_interface_admin'
    client = None
    host = None
    sample_type_match = None
    container_type_match = None
    template_match = None

    def ready(self):
        from .signals import senaite_sample_create_on_post_save
