import re
import json

from django.apps import apps as django_apps
from django.contrib.auth.decorators import login_required
from django.core.paginator import PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.urls import reverse
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
        sample_id = kwargs.get('sample_id', '')
        queryset = self.get_queryset()
        if sample_id == 'all':
            filter_val = request.GET.get('filter', None)
            if filter_val:
                filter_val = json.loads(filter_val)
                filter_val.pop('undefined', '')
                for key, value in filter_val.items():
                    queryset = queryset.filter(**{f'{key}__icontains': value})
            self.object_list = self.get_wrapped_queryset(queryset)
            page_size = request.GET.get('limit', 10)
            page_number = request.GET.get('offset', 1)
            paginator = self.get_paginator(self.object_list, page_size)
            try:
                page_obj = paginator.page(page_number)
            except PageNotAnInteger:
                page_obj = paginator.page(1)
            except EmptyPage:
                page_obj = paginator.page(paginator.num_pages)
            data = {
                'total': paginator.count,
                'rows': [{'id': obj.id,
                          'sample_id': obj.sample_id,
                          'participant_id': self.dashboard_link(obj.participant_id),
                          'sample_type': obj.specimen_type,
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
            'stored': self.stored,
            'collected': self.collected_samples.count(),
            'pending': self.pending_samples})
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

    def action_button(self, model_obj=None):
        btn_div = '<div class="btn-group btn-group-sm">'
        if model_obj.sample_status == 'resulted':
            btn_div = btn_div + (f'<a href="{model_obj.sample_results_file}" class="btn '
                                 'btn-outline-secondary"> <i class="fa fa-eye"></i> View Results </a>')
        elif model_obj.sample_status == 'stored':
            btn_div = btn_div + (f'<a href="{model_obj.storage_location}" class="btn '
                                 'btn-outline-secondary"> <i class="fa fa-eye"></i> View in Storage </a>')
        return btn_div + '</div>'

    def dashboard_link(self, participant_id=None, dashboard_url=''):
        url_link = reverse(dashboard_url, kwargs={'subject_identifier': participant_id})
        url_link = f'<a href="{url_link}"> {participant_id} </a>'
        return url_link
