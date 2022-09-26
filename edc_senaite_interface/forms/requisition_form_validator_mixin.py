from edc_form_validators import FormValidator
from edc_constants.constants import YES


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
