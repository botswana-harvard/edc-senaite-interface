import pytz
import re
from datetime import datetime
from django.apps import apps as django_apps
from django.core.exceptions import ValidationError
from edc_form_validators import FormValidator
from edc_constants.constants import YES
from requests import ConnectionError

from ..classes import SampleImporter
from ..models import SenaiteUser

app_config = django_apps.get_app_config('edc_senaite_interface')


class RequisitionFormValidatorMixin:

    def clean(self):
        cleaned_data = super().clean()
        self.validate_sample_id(cleaned_data=cleaned_data)
        return cleaned_data

    def validate_sample_id(self, cleaned_data=None):
        """
        If sample ID specified, connect to LIS via API and validate pattern of
        the sample ID matches LIS defined pattern i.e. {protocolNum}{stypeCode}{alphaCode}
        """
        form_validator = FormValidator(
            cleaned_data=cleaned_data,
            instance=self.instance)
        form_validator.required_if(
            YES,
            field='exists_on_lis',
            field_required='sample_id', )

        connection = SampleImporter(host=app_config.host)
        sample_id = self.cleaned_data.get('sample_id')
        panel = self.cleaned_data.get('panel')
        panel_name = panel.name if panel else None
        if self.authenticate_user(connection) and sample_id:
            # Get the sample type code for the client of the Sample
            client = self.search(
                connection, portal_type='Client', Title=app_config.client, complete=True)
            sample_match = app_config.sample_type_match.get(panel_name)
            sample_type = self.search(
                connection, portal_type='SampleType', catalog='bika_setup_catalog',
                Title=sample_match, complete=True)
            pattern = self.get_pattern(client, sample_type)
            # verify identifier matches correct pattern
            match = re.match(pattern, sample_id)
            if not match:
                raise ValidationError(
                    {'sample_id': 'Sample ID pattern is incorrect. Please correct.'})

            self.validate_sample_details_exists(connection, cleaned_data=cleaned_data)

    def validate_sample_details_exists(self, connection, cleaned_data=None):
        """
        If sample ID specified, connect to LIS via API and validate participant
        information for the sample ID provided i.e. PID, visit code, dob e.t.c.
        """
        sample_id = cleaned_data.get('sample_id')
        drawn_datetime = cleaned_data.get('drawn_datetime')
        query = {'catalog': 'bika_catalog_analysisrequest_listing',
                 'getId': sample_id,
                 'complete': True}

        ar = self.search(
            connection, portal_type='AnalysisRequest', **query)
        if ar:
            pid = ar[0].get('getParticipantID') == self.subject_identifier
            visit_code = ar[0].get('VisitCode') == self.visit_obj.visit_code
            lis_date_sampled = datetime.strptime(
                ''.join(ar[0].get('getDateSampled').rsplit(':', 1)), '%Y-%m-%dT%H:%M:%S%z')
            lis_date_sampled = lis_date_sampled.replace(tzinfo=None)
            drawn_datetime = drawn_datetime.astimezone(pytz.UTC)
            date_sampled = lis_date_sampled == drawn_datetime.replace(tzinfo=None, second=0)
            if not all([pid, visit_code, date_sampled]):
                raise ValidationError(
                    'Please check the Participant ID, visit code and/or date '
                    'sampled match data captured on the LIS')

    def search(self, importer, portal_type=None, **kwargs):
        query = {
            'portal_type': portal_type,
        }
        if kwargs:
            query.update(**kwargs)
        return importer.search(query)

    def get_pattern(self, client=None, sample_type=None):
        """ Define pattern for the sample ID i.e. {studyID}{stypeCode}{alphaCode}
        """
        study_number = client[0].get('TaxNumber') if client else None
        stype_codes = [stype.get('Prefix') for stype in sample_type]
        alphaCode = '[A-Z]{3}[0-9]{2}'

        return f"{study_number}({'|'.join(stype_codes)}){alphaCode}"

    def authenticate_user(self, connection):
        try:
            senaite_user = SenaiteUser.objects.get(
                related_username=self.current_user.username)
        except SenaiteUser.DoesNotExist:
            raise ValidationError('Senaite user does not exist.')
        else:
            try:
                authenticated = connection.auth(
                    senaite_user.username, senaite_user.password)
            except ConnectionError:
                if self.cleaned_data.get('exists_on_lis') == YES:
                    raise ValidationError('Failed to connect to the LIS')
                pass
            else:
                return authenticated
