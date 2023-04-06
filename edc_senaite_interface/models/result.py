from django.db import models
from edc_base.sites.site_model_mixin import SiteModelMixin
from edc_base.model_mixins import BaseUuidModel

from simple_history.models import HistoricalRecords
from ..model_mixins.result_model_mixin import SenaiteResultModelMixin, SenaiteResultValueMixin


class SenaiteResult(SenaiteResultModelMixin, SiteModelMixin, BaseUuidModel):

    history = HistoricalRecords()

    class Meta:
        app_label = 'edc_senaite_interface'
        verbose_name = 'Sample Result'


class SenaiteResultValue(SenaiteResultValueMixin, BaseUuidModel):

    result = models.ForeignKey(SenaiteResult, on_delete=models.PROTECT)

    history = HistoricalRecords()

    class Meta:
        unique_together = ('result', 'analysis_keyword')
        app_label = 'edc_senaite_interface'
        verbose_name = 'Analysis Result Value'
