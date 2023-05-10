from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist


class ResultModelWrapperMixin:

    result_model_wrapper_cls = None

    @property
    def result_model_obj(self):
        """Returns a senaite result model instance or None.
        """
        try:
            return self.result_model_cls.objects.get(
                **self.senaite_result_options)
        except ObjectDoesNotExist:
            return None

    @property
    def senaite_result(self):
        """Returns a wrapped saved or unsaved senaite result.
        """
        model_obj = self.result_model_obj or self.result_model_cls(
            **self.create_result_options)
        return self.result_model_wrapper_cls(model_obj=model_obj)

    @property
    def result_model_cls(self):
        return django_apps.get_model('edc_senaite_interface.senaiteresult')

    @property
    def create_result_options(self):
        """Returns a dictionary of options to create a new
        unpersisted senaite result model instance.
        """
        options = dict(
            sample_id=self.sample_id, )
        return options

    @property
    def senaite_result_options(self):
        """Returns a dictionary of options to get an existing
        senaite result instance.
        """
        options = dict(
            sample_id=self.sample_id, )
        return options

    @property
    def parent_id(self):
        if self.result_model_obj:
            return self.result_model_obj.parent_id
        return None

    @property
    def requisition_id(self):
        return getattr(self.requisition_obj, 'requisition_identifier', '')

    @property
    def participant_id(self):
        return getattr(self.requisition_obj, 'subject_identifier', '')

    @property
    def specimen_type(self):
        return getattr(self.requisition_obj, 'sample_type', '')

    @property
    def requisition_obj(self):
        if self.result_model_obj:
            model_obj = getattr(self.result_model_obj, 'requisition_obj', None)
            if not model_obj:
                model_obj = getattr(self.result_model_obj, 'primary_requisition', None)
            return model_obj
        return {}

    @property
    def result_pdf_link(self):
        url = ''
        if self.result_model_obj:
            results_pdf = getattr(self.result_model_obj, 'sample_results_file', None)
            url = results_pdf.url if results_pdf else ''
        return url
