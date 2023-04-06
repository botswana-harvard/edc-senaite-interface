from django.views.generic import TemplateView
from edc_base.view_mixins import EdcBaseViewMixin
from edc_navbar import NavbarViewMixin


class HomeView(EdcBaseViewMixin, NavbarViewMixin, TemplateView):
    template_name = 'edc_senaite_interface/home.html'
    navbar_name = 'edc_senaite_interface'
    navbar_selected_item = 'home'
