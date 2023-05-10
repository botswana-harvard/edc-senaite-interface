from django.conf import settings
from edc_model_wrapper import ModelWrapper
from .result_model_wrapper_mixin import ResultModelWrapperMixin


class ResultModelWrapper(ResultModelWrapperMixin, ModelWrapper):

    model = 'edc_senaite_interface.senaiteresult'
    next_url_name = settings.DASHBOARD_URL_NAMES.get(
        'senaite_result_listboard_url')
    next_url_attrs = ['sample_id', ]
    querystring_attrs = ['sample_id', ]

    @property
    def result_model_wrapper_cls(self):
        return self

    @property
    def dashboard_url(self):
        return ''
