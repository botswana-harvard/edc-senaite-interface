from django.contrib import admin
from edc_model_admin import audit_fieldset_tuple

from ..admin_site import edc_senaite_interface_admin
from ..forms import SenaiteResultForm
from ..models import SenaiteResult
from .base_admin_model_mixin import ModelAdminMixin


@admin.register(SenaiteResult, site=edc_senaite_interface_admin)
class SenaiteResultAdmin(ModelAdminMixin, admin.ModelAdmin):

    form = SenaiteResultForm

    fieldsets = (
        (None, {
            'fields': (
                'report_datetime',
                'sample_id',
                'sample_status',
                'is_partition',
                'parent_id',
                'storage_location',
                'date_stored')}),
        audit_fieldset_tuple
    )

    list_display = [
        'report_datetime', 'sample_id', 'sample_status', ]

    list_filter = [
        'sample_id', 'sample_status', 'report_datetime', ]

    radio_fields = {'sample_status': admin.VERTICAL}

    search_fields = (
        'sample_id',)
