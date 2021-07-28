from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, weak=False,
          dispatch_uid="senaite_sample_create_on_post_save")
def senaite_sample_create_on_post_save(
        sender, instance, raw, created, using, **kwargs):
    """Calls post_save method on the requisition instance.
    """
    if not raw:
        try:
            resp = instance.create_senaite_sample()
        except AttributeError as e:
            if 'create_senaite_sample' not in str(e):
                raise
        else:
            print(resp.json())
