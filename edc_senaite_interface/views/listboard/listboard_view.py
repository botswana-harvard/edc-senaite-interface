from django.apps import apps as django_apps
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from edc_base.view_mixins import EdcBaseViewMixin
from edc_dashboard.view_mixins import ListboardFilterViewMixin, SearchFormViewMixin
from edc_dashboard.views import ListboardView
from edc_navbar import NavbarViewMixin

from ..filters import ListboardViewFilters
from ...model_wrappers import ResultModelWrapper


class ListboardView(NavbarViewMixin, EdcBaseViewMixin,
                    ListboardFilterViewMixin, SearchFormViewMixin,
                    ListboardView):

    listboard_template = 'senaite_result_listboard_template'
    listboard_url = 'senaite_result_listboard_url'

    model = 'edc_senaite_interface.senaiteresult'
    model_wrapper_cls = ResultModelWrapper
    listboard_view_filters = ListboardViewFilters()
    navbar_name = 'edc_senaite_interface'
    navbar_selected_item = 'senaite_result'
    search_form_url = 'senaite_result_listboard_url'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'resulted': self.resulted,
            'stored': self.stored,
            'collected': self.collected_samples.count(),
            'pending': self.pending_samples})
        return context

    @property
    def resulted(self):
        samples = self.get_queryset()
        return samples.filter(sample_status='resulted')

    @property
    def stored(self):
        samples = self.get_queryset()
        return samples.filter(sample_status='stored')

    @property
    def collected_samples(self):
        result_model_cls = django_apps.get_model(self.model)
        requisition_model = result_model_cls.requisition_model
        requisition_model_cls = django_apps.get_model(requisition_model)

        return requisition_model_cls.objects.all()

    @property
    def pending_samples(self):
        result_objs = self.get_queryset().values_list('sample_id', flat=True)

        pending = self.collected_samples.exclude(sample_id__in=result_objs)
        return pending.count()
