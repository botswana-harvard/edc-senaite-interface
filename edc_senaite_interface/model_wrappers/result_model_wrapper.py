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

    @property
    def results_objs(self):
        if self.object:
            return self.object.senaiteresultvalue_set.all()

    @property
    def visit_code(self):
        requisition = None
        if self.object:
            requisition = self.object.requisition_obj or self.object.primary_requisition
        return getattr(requisition, 'visit_code', '')
