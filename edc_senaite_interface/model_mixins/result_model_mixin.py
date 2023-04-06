from django.apps import apps as django_apps
from django.db import models
from edc_base.model_validators.date import datetime_not_future
from edc_base.utils import get_utcnow
from edc_protocol.validators import datetime_not_before_study_start

SAMPLE_STATUS = (
    ('resulted', 'Resulted'),
    ('stored', 'Stored'),
    ('pending', 'Pending'),
)


class SenaiteResultModelMixin(models.Model):
    """ Mixin defining attributes for capturing result details once a requisition
        is resulted or stored on the LIMS system.
    """

    requisition_model = None

    report_datetime = models.DateTimeField(
        verbose_name='Date and Time captured',
        default=get_utcnow,
        validators=[datetime_not_future, datetime_not_before_study_start])

    sample_id = models.CharField(
        verbose_name='LIS generated sample ID',
        max_length=50,
        unique=True, )

    sample_status = models.CharField(
        verbose_name='Status',
        max_length=50,
        choices=SAMPLE_STATUS,
        default='resulted', )

    is_partition = models.BooleanField(default=False)

    parent_id = models.CharField(
        verbose_name='Primary sample ID, if partition',
        max_length=50,
        null=True)

    # Storage information
    storage_location = models.CharField(
        verbose_name='Physical location of sample in storage.',
        max_length=100,
        null=True, )

    date_stored = models.DateField(null=True)

    @property
    def requisition_model_cls(self):
        return django_apps.get_model(self.requisition_model)

    @property
    def primary_requisition(self):
        if self.parent_id:
            return self.get_requisition(sample_id=self.parent_id)
        return None

    @property
    def requisition_obj(self):
        return self.get_requisition(sample_id=self.sample_id)

    def get_requisition(self, sample_id=None):
        try:
            model_obj = self.requisition_model_cls.objects.get(
                sample_id=sample_id)
        except self.requisition_model_cls.DoesNotExist:
            return None
        else:
            return model_obj

    def __str__(self):
        return f'{self.sample_id}, status: {self.sample_status}'

    class Meta:
        abstract = True


class SenaiteResultValueMixin(models.Model):

    analysis_title = models.CharField(
        verbose_name='Name of analysis/test resulted',
        max_length=50, )

    analysis_keyword = models.CharField(
        verbose_name='Unique keyword used to identify the analysis',
        max_length=50, )

    result_value = models.CharField(max_length=50)

    result_unit = models.CharField(
        verbose_name='Unit of result value e.g. (gm/dL)',
        max_length=10,
        null=True, )

    reference_values = models.CharField(
        verbose_name='Result reference values (lower-upper limit)',
        max_length=50,
        null=True, )

    out_range = models.BooleanField(default=False)

    date_resulted = models.DateField()

    def __str__(self):
        return f'{self.analysis_title}, result: {self.result_value}'

    class Meta:
        abstract = True
