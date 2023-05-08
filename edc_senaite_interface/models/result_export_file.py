from django.db import models
from edc_base.sites.site_model_mixin import SiteModelMixin
from edc_base.model_mixins import BaseUuidModel
from edc_base.utils import get_utcnow


class ResultExportFile(SiteModelMixin, BaseUuidModel):

    document = models.FileField(upload_to='documents/')

    date_generated = models.DateField(default=get_utcnow)

    @property
    def file_url(self):
        """Return the file url.
        """
        try:
            return self.document.url
        except ValueError:
            return None

    class Meta:
        app_label = 'edc_senaite_interface'
