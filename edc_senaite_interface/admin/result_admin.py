from django.contrib import admin
from edc_model_admin import audit_fieldset_tuple

from ..admin_site import edc_senaite_interface_admin
from ..forms import SenaiteUserForm
from ..models import SenaiteResult
from .base_admin_model_mixin import ModelAdminMixin


@admin.register(SenaiteResult, site=edc_senaite_interface_admin)
