from django.contrib import admin
from edc_model_admin import audit_fieldset_tuple

from .base_admin_model_mixin import ModelAdminMixin


class SenaiteResultAdminMixin(ModelAdminMixin, admin.ModelAdmin):

    fieldsets = (
        (None, {
            'fields': (
                'report_datetime',
                'sample_id',
                'sample_status',
                'is_partition',
                'parent_id',
                'storage_location',
                'date_stored',
                'sample_results_file')}),
        audit_fieldset_tuple
    )

    list_display = [
        'report_datetime', 'sample_id', 'sample_status', ]

    list_filter = [
        'sample_id', 'sample_status', 'report_datetime', ]

    radio_fields = {'sample_status': admin.VERTICAL}

    search_fields = (
        'sample_id',)
