import re

from django.contrib.auth.decorators import login_required
from django.core.paginator import PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.utils.decorators import method_decorator
from edc_base.view_mixins import EdcBaseViewMixin
from edc_dashboard.view_mixins import ListboardFilterViewMixin, SearchFormViewMixin
from edc_dashboard.views import ListboardView
from edc_navbar import NavbarViewMixin

from ..filters import ListboardViewFilters
from ...model_wrappers import ResultModelWrapper
from django.http.response import JsonResponse


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

    def get(self, request, *args, **kwargs):
        sample_id = kwargs.get('sample_id')
        if sample_id == 'all':
            self.object_list = self.get_wrapped_queryset(self.get_queryset())
            paginator = self.get_paginator(self.object_list, self.paginate_by)
            page = request.GET.get('page')
            try:
                page_obj = paginator.page(page)
            except PageNotAnInteger:
                page_obj = paginator.page(1)
            except EmptyPage:
                page_obj = paginator.page(paginator.num_pages)
            data = {
                'total': paginator.count,
                'rows': [{'id': obj.id,
                          'sample_id': obj.sample_id,
                          'participant_id': obj.participant_id,
                          'sample_status': obj.sample_status,
                          'date_stored': obj.date_stored,
                          'is_partition': obj.is_partition,
                          'parent_id': obj.parent_id,
                          'requisition_id': obj.requisition_id,
                          'view_results': self.action_button(model_obj=obj)} for obj in page_obj]}
            return JsonResponse(data)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'resulted': self.resulted,
            'stored': self.stored})
        return context

    def extra_search_options(self, search_term):
        q = Q()
        if re.match('^[A-Z]+$', search_term):
            q = Q(first_name__exact=search_term)
        return q

    @property
    def resulted(self):
        samples = self.get_queryset()
        return samples.filter(sample_status='resulted')

    @property
    def stored(self):
        samples = self.get_queryset()
        return samples.filter(sample_status='stored')

    def action_button(self, model_obj=None):
        btn_div = '<div class="btn-group btn-group-sm">'
        if model_obj.sample_status == 'resulted':
            btn_div = btn_div + (f'<a href="{model_obj.sample_results_file}" class="btn '
                                 'btn-outline-secondary"> <i class="fa fa-eye"></i> View Results </a>')
        elif model_obj.sample_status == 'stored':
            btn_div = btn_div + (f'<a href="{model_obj.storage_location}" class="btn '
                                 'btn-outline-secondary"> <i class="fa fa-eye"></i> View in Storage </a>')
        return btn_div + '</div>'
