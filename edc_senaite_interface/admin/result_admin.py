from django.contrib import admin


from ..admin_site import edc_senaite_interface_admin
from ..forms import SenaiteResultForm
from ..models import SenaiteResult
from .result_model_admin_mixin import SenaiteResultAdminMixin


@admin.register(SenaiteResult, site=edc_senaite_interface_admin)
class SenaiteResultAdmin(SenaiteResultAdminMixin, admin.ModelAdmin):

    form = SenaiteResultForm
