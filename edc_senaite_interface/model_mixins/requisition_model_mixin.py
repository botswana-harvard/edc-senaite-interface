from django.apps import apps as django_apps
from django.db import models

from ..classes import SampleImporter
from ..exceptions import EdcSenaiteInterfaceError
from ..models import SenaiteUser

app_config = django_apps.get_app_config('edc_senaite_interface')


class SenaiteRequisitionModelMixin(models.Model):

    consent_model = None  # td_maternal.subjectconset
    visit_model_attr = None    # maternal_visit

    sample_id = models.CharField(
        verbose_name="LIS generated Sample Identifier",
        max_length=50)

    def data(self):
        data = {}
        data.update(
            Client=app_config.client,
            Contact=self.contact,
            SampleType=self.sample_type,
            DateSampled=self.drawn_datetime.strftime("%Y-%m-%d %H:%M"),
            Template=self.template,
            DefaultContainerType=self.default_container_type,
            ParticipantID=self.subject_identifier,
            ParticipantInitials=self.initials,
            Gender=self.gender,
            Visit=self.visit_code,
            VisitCode=self.visit_code,
            DateOfBirth=self.dob,
            Volume=f'{self.estimated_volume}mL')
        return data

    def create_senaite_sample(self):

        importer = SampleImporter()
        if importer.auth(self.senaite_username, self.senaite_password):
            return importer.create_sample(data=self.data())
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
        self.consent_obj.gender

    @property
    def dob(self):
        self.consent_obj.dob

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
            SenaiteUser.objects.get(username=self.user_created)
        except SenaiteUser.DoesNotExist:
            raise EdcSenaiteInterfaceError(
                f'Senaite user infor for {self.user_created}')
        else:
            return self.user_created

    @property
    def senaite_password(self):
        """Return a senate password.
        """
        try:
            senaite_user = SenaiteUser.objects.get(username=self.user_created)
        except SenaiteUser.DoesNotExist:
            raise EdcSenaiteInterfaceError(
                f'Senaite user infor for {self.user_created} does not exist.')
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
            senaite_user = SenaiteUser.objects.get(username=self.user_created)
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

    class Meta:
        abstract = True