from django.contrib import admin
from django.contrib import messages

from ..models import SenaiteUser


class SenaiteRequisitionAdminMixin(admin.ModelAdmin):

    def save_model(self, request, obj, form, change):
        if not change:
            user_created = obj.user_created or request.user.username
            try:
                SenaiteUser.objects.get(username=user_created)
            except SenaiteUser.DoesNotExist:
                msg = (f'Senaite user infor for {user_created}. '
                       'Sample not created on the LIS')
                messages.add_message(
                    request, messages.SUCCESS, msg)
        super().save_model(request, obj, form, change)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.current_user = request.user
        return form
