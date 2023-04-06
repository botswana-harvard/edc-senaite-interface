import re

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.utils.decorators import method_decorator
from edc_base.view_mixins import EdcBaseViewMixin
from edc_dashboard.view_mixins import ListboardFilterViewMixin, SearchFormViewMixin
from edc_dashboard.views import ListboardView
from edc_navbar import NavbarViewMixin

from ..filters import ListboardViewFilters
from ...model_wrappers import ResultModelWrapper


class ListboardView(EdcBaseViewMixin, NavbarViewMixin,
                    ListboardFilterViewMixin, SearchFormViewMixin,
                    ListboardView):

    listboard_template = 'senaite_result_listboard_template'
    listboard_url = 'senaite_result_listboard_url'
    listboard_panel_style = 'success'
    listboard_fa_icon = 'fa fa-list-alt'

    model = 'edc_senaite_interface.senaiteresult'
    model_wrapper_cls = ResultModelWrapper
    listboard_view_filters = ListboardViewFilters()
    navbar_name = 'edc_senaite_interface'
    navbar_selected_item = 'senaite_result'
    search_form_url = 'senaite_result_listboard_url'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

#     def get_queryset_filter_options(self, request, *args, **kwargs):
#         options = super().get_queryset_filter_options(request, *args, **kwargs)
#         if kwargs.get('order_number'):
#             options.update(
#                 {'order_number': kwargs.get('order_number')})
#         payment_filter = options.get('invoicepaid__is', '')
#         if 'invoicepaid__is' in options:
#             options.pop('invoicepaid__is')
#             ids = self.purchaseinvoice_ids(payment_filter)
#             options.update({'order_number__in': ids})
#         return options

    def extra_search_options(self, search_term):
        q = Q()
        if re.match('^[A-Z]+$', search_term):
            q = Q(first_name__exact=search_term)
        return q
