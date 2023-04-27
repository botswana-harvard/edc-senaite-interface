"""EDC senaite interface URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path
from django.views.generic.base import RedirectView

from .admin_site import edc_senaite_interface_admin
from .views import ListboardView
from .url_config import UrlConfig


app_name = 'edc_senaite_interface'

senaite_result_listboard_url_config = UrlConfig(
    url_name='senaite_result_listboard_url',
    view_class=ListboardView,
    label='senaite_result_listboard',
    identifier_label='sample_id',
    identifier_pattern='[a-zA-Z0-9]+')


urlpatterns = [
    path('admin/', edc_senaite_interface_admin.urls),
    path('', RedirectView.as_view(url='admin/'), name='home_url'),
]

urlpatterns += senaite_result_listboard_url_config.listboard_urls
