from django.urls.conf import re_path
from edc_dashboard import UrlConfig as BaseUrlConfig


class UrlConfig(BaseUrlConfig):

    @property
    def listboard_urls(self):
        """Returns url patterns.

        configs = [(listboard_url, listboard_view_class, label), (), ...]
        """
        urlpatterns = [
            re_path(r'^' + f'{self.label}/'
                    f'(?P<{self.identifier_label}>{self.identifier_pattern})/(?P<refresh>True|False)/(?P<page>\d+)/',
                    self.view_class.as_view(), name=self.url_name),
            re_path(r'^' + f'{self.label}/'
                    f'(?P<{self.identifier_label}>{self.identifier_pattern})/(?P<refresh>True|False)/',
                    self.view_class.as_view(), name=self.url_name),
            re_path(r'^' + f'{self.label}/'
                    f'(?P<{self.identifier_label}>{self.identifier_pattern})/(?P<page>\d+)/',
                    self.view_class.as_view(), name=self.url_name),
            re_path(r'^' + f'{self.label}/'
                    f'(?P<{self.identifier_label}>{self.identifier_pattern})/',
                    self.view_class.as_view(), name=self.url_name),
#             re_path(r'^' + f'{self.label}/(?P<refresh>True|False)/(?P<page>\d+)/',
#                     self.view_class.as_view(), name=self.url_name),
            re_path(r'^' + f'{self.label}/(?P<page>\d+)/',
                    self.view_class.as_view(), name=self.url_name),
#             re_path(r'^' + f'{self.label}/(?P<refresh>True|False)/',
#                     self.view_class.as_view(), name=self.url_name),
            re_path(r'^' + f'{self.label}/',
                    self.view_class.as_view(), name=self.url_name)]
        return urlpatterns
