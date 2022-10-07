import re
from django.apps import apps as django_apps
from django.core.exceptions import ValidationError
from django.db.models import Q
from edc_form_validators import FormValidator
from edc_constants.constants import YES

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
        """
        form_validator = FormValidator(
            cleaned_data=cleaned_data,
            instance=self.instance)
        form_validator.required_if(
            YES,
            field='exists_on_lis',
            field_required='sample_id', )

        sample_id = self.cleaned_data.get('sample_id')
        panel = self.cleaned_data.get('panel')
        panel_name = panel.name if panel else None
        connection = SampleImporter(host=app_config.host)
        if self.authenticate_user(connection):
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
            return connection.auth(senaite_user.username, senaite_user.password)
