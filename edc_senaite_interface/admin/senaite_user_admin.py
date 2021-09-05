from django.contrib import admin
from edc_model_admin import audit_fieldset_tuple

from ..admin_site import edc_senaite_interface_admin
from ..forms import SenaiteUserForm
from ..models import SenaiteUser
from .base_admin_model_mixin import ModelAdminMixin


@admin.register(SenaiteUser, site=edc_senaite_interface_admin)
class SenaiteUserAdmin(ModelAdminMixin, admin.ModelAdmin):

    form = SenaiteUserForm

    fieldsets = (
        (None, {
            'fields': (
                'username',
                'password')}),
        audit_fieldset_tuple
    )

    list_display = [
        'username', 'user_created', 'user_modified', 'modified']

    list_filter = [
        'created', 'user_created', 'modified', 'user_modified']

    search_fields = (
        'username',)
