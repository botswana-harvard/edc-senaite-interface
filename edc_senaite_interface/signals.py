from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, weak=False,
          dispatch_uid="senaite_sample_create_on_post_save")
def senaite_sample_create_on_post_save(
        sender, instance, raw, created, using, **kwargs):
    """Calls post_save method on the requisition instance.
    """
    if not raw:
        if created:
            try:
                resp = instance.save_senaite_sample()
            except AttributeError as e:
                if 'save_senaite_sample' not in str(e):
                    raise
            else:
                resp_dict = resp.json()
                sample_items = resp_dict.get('items', [])
                sample_id = sample_items[0].get('id') if sample_items else None
                instance.sample_id = sample_id
                instance.save_base(raw=True)
        else:
            try:
                resp = instance.save_senaite_sample(method='update')
            except AttributeError as e:
                if 'save_senaite_sample' not in str(e):
                    raise
