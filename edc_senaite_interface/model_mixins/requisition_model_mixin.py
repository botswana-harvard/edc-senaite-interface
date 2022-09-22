from django.apps import apps as django_apps
from django.db import models
from django.db.models import Q
from edc_constants.constants import NO
from edc_constants.choices import YES_NO

from ..classes import SampleImporter
from ..exceptions import EdcSenaiteInterfaceError
from ..models import SenaiteUser

app_config = django_apps.get_app_config('edc_senaite_interface')


class SenaiteRequisitionModelMixin(models.Model):

    consent_model = None  # td_maternal.subjectconset
    visit_model_attr = None    # maternal_visit

    sample_id = models.CharField(
        verbose_name="LIS generated Sample Identifier",
        max_length=50,
        blank=True)

    exists_on_lis = models.CharField(
        verbose_name='Already exists on LIS?',
        max_length=3,
        choices=YES_NO,
        default=NO)

    @property
    def data(self):
        data = {}
        data.update(
            Client=app_config.client,
            Contact=self.contact,
            Courier=app_config.courier,
            SampleType=self.sample_type,
            DateSampled=self.drawn_datetime.strftime("%Y-%m-%d %H:%M"),
            Template=self.template,
            DefaultContainerType=self.default_container_type,
            ParticipantID=self.subject_identifier,
            ParticipantInitials=self.initials,
            ClientSampleID=self.requisition_identifier,
            Gender=self.gender.lower(),
            Visit=self.visit_code,
            VisitCode=self.visit_code,
            DateOfBirth=self.dob.strftime("%Y-%m-%d"),
            Volume=str(self.estimated_volume),
            Remarks=self.remarks,
            Priority=self.senaite_priority)
        return data

    def save_senaite_sample(self, method='create'):
        importer = SampleImporter(host=app_config.host)
        if importer.auth(self.senaite_username, self.senaite_password):
            if method == 'create':
                return importer.create_sample(data=self.data)
            elif method == 'update':
                sample_id = self.sample_id
                return importer.update_sample(identifier=sample_id, data=self.data)
        else:
            print("Cannot authenticate")

    @property
    def consent_obj(self):
        consent = django_apps.get_model(
            self.consent_model).objects.filter(
                subject_identifier=self.subject_identifier).last()
        return consent

    @property
    def initials(self):
        return self.consent_obj.initials

    @property
    def gender(self):
        return self.consent_obj.gender

    @property
    def dob(self):
        return self.consent_obj.dob

    @property
    def visit(self):
        return getattr(self, self.visit_model_attr)

    @property
    def visit_code(self):
        return self.visit.visit_code

    @property
    def senaite_username(self):
        """Returns a senaite username.
        """
        try:
            senaite_user = SenaiteUser.objects.get(
                Q(related_username=self.user_created) | Q(related_username=self.user_modified))
        except SenaiteUser.DoesNotExist:
            pass
        else:
            return senaite_user.username

    @property
    def senaite_password(self):
        """Return a senaite password.
        """
        try:
            senaite_user = SenaiteUser.objects.get(
                Q(related_username=self.user_created) | Q(related_username=self.user_modified))
        except SenaiteUser.DoesNotExist:
            pass
        else:
            return senaite_user.password

    @property
    def sample_type(self):
        """Returnn the sample type.
        Overide this method to match the sample type used on the EDC
        with the one onn Senaite LIMS.
        """
        panel_name = self.panel.name
        return app_config.sample_type_match.get(panel_name, None)

    @property
    def contact(self):
        """Return the LIS contact. Override to return the matching value on the LIS.
        """
        try:
            senaite_user = SenaiteUser.objects.get(
                Q(related_username=self.user_created) | Q(related_username=self.user_modified))
        except SenaiteUser.DoesNotExist:
            raise EdcSenaiteInterfaceError(
                f'Senaite user infor for {self.user_created} does not exist.')
        else:
            return senaite_user.contact

    @property
    def template(self):
        """Return the LIS template to query the LIS.
        Override this to match the LIS value.
        """
        return app_config.template_match.get(
            self.panel.name, None)

    @property
    def default_container_type(self):
        """Return the LIS container type to query the LIS.
        Override this to match the LIS value.
        """
        return app_config.container_type_match.get(
            self.panel.name, None)

    @property
    def remarks(self):
        prev_req = self.history.latest().prev_record
        if prev_req:
            return None if self.comments in self.history.exclude(
                history_id=prev_req.history_id).values_list(
                    'comments', flat=True) else self.comments
        return self.comments

    @property
    def senaite_priority(self):
        """Default to normal, maps to '3' for routine on LIS. Override per
        project to set priority mapping.
        """
        return '3'

    class Meta:
        abstract = True
