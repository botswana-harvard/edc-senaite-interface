from django.apps import apps as django_apps
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from edc_constants.constants import YES


app_config = django_apps.get_app_config('edc_senaite_interface')


@receiver(post_save, weak=False,
          dispatch_uid="senaite_sample_create_on_post_save")
def senaite_sample_create_on_post_save(
        sender, instance, raw, created, using, **kwargs):
    """Calls post_save method on the requisition instance.
    """
    if not raw:
        device_role = settings.DEVICE_ROLE
        device_id = settings.DEVICE_ID
        if (device_role == app_config.DEVICE_ROLE and
                device_id == app_config.DEVICE_ID):
            if not getattr(instance, 'sample_id', None):
                create_new_senaite_sample(instance=instance)
                return
            try:
                resp = instance.save_senaite_sample(method='update')
            except AttributeError as e:
                if 'save_senaite_sample' not in str(e):
                    raise


def create_new_senaite_sample(instance=None):
    if getattr(instance, 'is_drawn', None) == YES:
        try:
            resp = instance.save_senaite_sample()
        except AttributeError as e:
            if 'save_senaite_sample' not in str(e):
                raise
        else:
            if resp:
                resp_dict = resp.json()
                sample_items = resp_dict.get('items', [])
                sample_id = sample_items[0].get('id') if sample_items else None
                instance.sample_id = sample_id
                instance.exists_on_lis = YES
                instance.save_base(raw=True)
            else:
                return
