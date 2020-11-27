from django.conf import settings
from django.db import models
from django.db.models.deletion import PROTECT
from edc_base.model_managers import HistoricalRecords
from edc_base.model_mixins import BaseUuidModel
from edc_constants.constants import NOT_APPLICABLE
from edc_lab.choices import PRIORITY
from edc_lab.models import RequisitionIdentifierMixin
from edc_lab.models import RequisitionModelMixin, RequisitionStatusMixin
from edc_search.model_mixins import SearchSlugManager
from edc_visit_tracking.managers import CrfModelManager as VisitTrackingCrfModelManager
from edc_visit_tracking.model_mixins import CrfModelMixin as VisitTrackingCrfModelMixin
from edc_visit_tracking.model_mixins import PreviousVisitModelMixin

from edc_appointment.models import Appointment
from edc_visit_tracking.choices import VISIT_REASON
from edc_visit_tracking.managers import VisitModelManager
from edc_visit_tracking.model_mixins import VisitModelMixin, CaretakerFieldsMixin

from edc_base.model_validators import date_not_future
from edc_constants.choices import YES_NO
from edc_constants.constants import ALIVE, PARTICIPANT
from edc_protocol.validators import date_not_before_study_start
from edc_constants.constants import (
    OFF_STUDY, ON_STUDY)


from edc_visit_schedule.model_mixins import SubjectScheduleCrfModelMixin

from ..model_mixins import SenaiteRequisitionModelMixin



VISIT_STUDY_STATUS = (
    (ON_STUDY, 'On study'),
    (OFF_STUDY,
     'Off study-no further follow-up (including death); use only '
     'for last study contact'),
)


class CurrentSiteManager(VisitModelManager):
    pass


class SubjectVisit(VisitModelMixin,
                    CaretakerFieldsMixin, BaseUuidModel):

    """ subject visit form that links all follow-up forms
    """

    appointment = models.OneToOneField(Appointment, on_delete=models.PROTECT)

    reason = models.CharField(
        verbose_name='Reason for visit',
        max_length=25,
        choices=VISIT_REASON)

    reason_missed = models.CharField(
        verbose_name=(
            'If \'missed\' above, reason scheduled '
            'scheduled visit was missed'),
        blank=True,
        null=True,
        max_length=250)

    covid_visit = models.CharField(
        verbose_name=('Is this a telephonic visit that is occurring '
                      'during COVID-19?'),
        max_length=3,
        choices=YES_NO)

    reason_unscheduled = models.CharField(
        verbose_name=(
            'If \'Unscheduled\' above, provide reason for '
            'the unscheduled visit'),
        blank=True,
        null=True,
        max_length=25,)

    study_status = models.CharField(
        verbose_name="What is the participant's current study status",
        max_length=50,
        choices=VISIT_STUDY_STATUS)

    survival_status = models.CharField(
        max_length=10,
        verbose_name='Participant\'s survival status',
        null=True,
        default=ALIVE)

    info_source = models.CharField(
        verbose_name='Source of information?',
        default=PARTICIPANT,
        max_length=25)

    last_alive_date = models.DateField(
        verbose_name='Date participant last known alive',
        blank=True,
        null=True,
        validators=[date_not_before_study_start, date_not_future])

    on_site = CurrentSiteManager()

    objects = VisitModelManager()

    history = HistoricalRecords()

    class Meta(VisitModelMixin.Meta):
        app_label = 'edc_senaite_interface'
        verbose_name = 'Subject Visit'



class Manager(VisitTrackingCrfModelManager, SearchSlugManager):
    pass


class SubjectRequisition(
        RequisitionModelMixin, RequisitionStatusMixin, RequisitionIdentifierMixin,
        VisitTrackingCrfModelMixin, SubjectScheduleCrfModelMixin,
        PreviousVisitModelMixin, SenaiteRequisitionModelMixin, BaseUuidModel):    

    subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)

    subject_identifier = models.CharField(
        verbose_name="Subject Identifier",
        max_length=50)

    study_site = models.CharField(
        verbose_name='Study site',
        max_length=25)

    estimated_volume = models.DecimalField(
        verbose_name='Estimated volume in mL',
        max_digits=7,
        decimal_places=2,
        help_text=(
            'If applicable, estimated volume of sample for this test/order. '
            'This is the total volume if number of "tubes" above is greater than 1'))

    item_count = models.IntegerField(
        verbose_name='Total number of items',
        help_text=(
            'Number of tubes, samples, cards, etc being sent for this test/order only. '
            'Determines number of labels to print'))

    priority = models.CharField(
        verbose_name='Priority',
        max_length=25,
        choices=PRIORITY,
        default='normal',)

    reason_not_drawn = models.CharField(
        verbose_name='If not drawn, please explain',
        max_length=25,
        default=NOT_APPLICABLE)

    comments = models.TextField(
        max_length=350,
        null=True,
        blank=True)

#     on_site = CurrentSiteManager()

    objects = Manager()

    history = HistoricalRecords()

    def __str__(self):
        return (
            f'{self.requisition_identifier} '
            f'{self.panel_object.verbose_name}')

    def save(self, *args, **kwargs):
        self.report_datetime = self.requisition_datetime
        self.subject_identifier = self.subject_visit.subject_identifier
        super().save(*args, **kwargs)

    @property
    def sample_type(self):
        """Returnn the sample type.
        Overide this method to match the sample type used on the EDC
        with the one onn Senaite LIMS.
        """
        return None

    def get_search_slug_fields(self):
        fields = super().get_search_slug_fields()
        fields.extend([
            'requisition_identifier',
            'human_readable_identifier', 'identifier_prefix'])
        return fields

    class Meta:
        unique_together = ('panel', 'subject_visit')
