from django.contrib import admin
from django.contrib import messages

from ..models import SenaiteUser


class SenaiteRequisitionAdminMixin(admin.ModelAdmin):

    def save_model(self, request, obj, form, change):
        if not change:
            username = getattr(obj, 'user_created', None)
            try:
                SenaiteUser.objects.get(related_username=username)
            except SenaiteUser.DoesNotExist:
                username = request.user.username if getattr(request, 'user', None) else None
                try:
                    SenaiteUser.objects.get(related_username=username)
                except SenaiteUser.DoesNotExist:
                    msg = (f'Senaite user account for {username} does not exist.'
                           'Sample not created on the LIS')
                    messages.add_message(
                        request, messages.ERROR, msg)
        super().save_model(request, obj, form, change)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.current_user = request.user
        return form
