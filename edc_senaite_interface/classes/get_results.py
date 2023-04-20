import uuid
from datetime import datetime
from django.apps import apps as django_apps
from edc_constants.constants import POS, NEG, IND

from .api_resolvers_mixin import APIResolversMixin

app_config = django_apps.get_app_config('edc_senaite_interface')


class AnalysisResult(APIResolversMixin):

    senaite_result_model = 'edc_senaite_interface.senaiteresult'
    senaite_result_value_model = 'edc_senaite_interface.senaiteresultvalue'

    def __init__(self, host=None, result_model=None, result_value_model=None):
        self.host = host or app_config.host
        self.result_model = result_model or self.senaite_result_model
        self.result_value_model = result_value_model or self.senaite_result_value_model

    @property
    def result_model_cls(self):
        return django_apps.get_model(self.result_model)

    @property
    def result_value_cls(self):
        return django_apps.get_model(self.result_value_model)

    def create_result_obj(self, sample_id=None, params={}):
        """ Update an existing result instance for the given `sample_id` or create
            a result to capture the result values for a published or stored sample.
            @param sample_id: LIS generated identifier
            @return: result object if created else None
        """
        if params:
            obj, _ = self.result_model_cls.objects.update_or_create(
                sample_id=sample_id,
                defaults=params)
            return obj
        return None

    def create_result_params(self, data={}):
        """ Create parameters to populate the result object for the specific sampleID
            @param data: A dictionary of the sample details
        """
        params = {}
        review_state = data.get('review_state', '')
        if review_state in ['stored', 'published']:
            if review_state == 'published':
                params.update(sample_status='resulted', )
            elif review_state == 'stored':
                date_str = data.get('getDateStored', '')
                stored_dt = datetime.strptime(date_str, '%Y-%m-%d %H:%M')
                params.update(sample_status='stored',
                              storage_location=data.get('getSamplesContainerURL', ''),
                              date_stored=stored_dt.date(), )

            parent_ar = data.get('ParentAnalysisRequest', {}) or {}
            detached_ar = data.get('DetachedFrom', {}) or {}
            parent_details = parent_ar or detached_ar
            partition = self.check_uuid(parent_details.get('uid', ''))
            if partition:
                primary_id = self.get_parent_id(parent_details)
                params.update(is_partition=partition,
                              parent_id=primary_id)
        return params

    def create_items_params(self, data={}):
        """ Create parameters to populate the result values object for a specific
            parent result instance.
            @param data: A dictionary of the result details
        """
        params = {'analysis_title': data.get('title', ''),
                  'result_unit': data.get('Unit', None), }

        result_options = data.get('ResultOptions', []) or []
        result = data.get('Result', '')
        for option in result_options:
            if option.get('ResultValue') == result:
                result = option.get('ResultText')
                break

        result_dt_str = data.get('ResultCaptureDate', '')
        result_dt = datetime.strptime(
            ''.join(result_dt_str.rsplit(':', 1)), '%Y-%m-%dT%H:%M:%S%z')
        params.update(result_value=result,
                      date_resulted=result_dt.date())
        return params

    def create_result_items(self, result=None, data={}):
        """ Update an existing result value for a given `result` obj or create
            result values to capture the details of analysis tested.
            @param result: related result object
            @param data: sample data containing details for the analyses tested 
        """
        analyses = data.get('Analyses')
        for analysis in analyses:
            analysis_data = self.get_items(analysis.get('api_url', ''))
            if analysis_data:
                analysis_data = analysis_data[0]
                create_values = self.create_items_params(data=analysis_data)
                obj, _ = self.result_value_cls.objects.update_or_create(
                    result=result,
                    analysis_keyword=analysis_data.get('Keyword'),
                    defaults=create_values)

    def get_sample_results(self, sample_id=None, partitions=[]):
        """ Retrieve analyses results for a published or stored sample and create
            relevant result model instances for a given sample_id.
            @param sample_id: LIS generated or UUID for a sample.
            @param partitions: UUIDs for the partitions if sample aliquoted.
        """
        sample_query = {'complete': True,
                        'catalog': 'bika_catalog_analysisrequest_listing', }
        is_uuid = self.check_uuid(sample_id)
        if is_uuid:
            sample_query.update(UID=sample_id)
        else:
            sample_query.update(id=sample_id)

        response = self.search(sample_query)
        sample_details = response[0] if response else {}

        create_values = self.create_result_params(data=sample_details)

        lis_gen_id = sample_details.get('id', '')

        model_obj = self.create_result_obj(
            sample_id=lis_gen_id, params=create_values, )

        if model_obj and getattr(model_obj, 'sample_status', '') == 'resulted':
            self.create_result_items(result=model_obj, data=sample_details)
            self.download_results_file(obj=model_obj, data=sample_details)

        if not partitions:
            partitions = sample_details.get('getDescendantsUIDs', [])
        while len(partitions) > 0:
            sample_id = partitions.pop(0)
            self.get_sample_results(sample_id, partitions)

    def check_uuid(self, sample_id=None):
        """ Check if sample ID provided is UUID or LIS generated identifier
        @param sample_id: sample identifier (either valid UUID or LIS generated)
        @return: True if UUID else False
        """
        try:
            uuid.UUID(str(sample_id))
            return True
        except ValueError:
            return False

    def get_parent_id(self, parent_ar={}):
        """ Retrieve the parent LIS generated sample identifier, send a GET request
            to the @search endpoint of the API with the UUID and retrieve the id
            of the sample.
            @param parent_ar: details of the parent/primary sample.
            @return: sample ID
        """
        items = self.get_items(url=parent_ar.get('api_url', ''))
        return items[0].get('id') if items else None

    def download_results_file(self, obj=None, data={}):
        """ Retrieve url for the published results file, and download the content
            to upload to the result instance.
            @param obj: result instance
            @param data: sample details
        """
        sample_uid = data.get('uid', '')
        query = {'portal_type': 'ARReport',
                 'sample_uid': sample_uid,
                 'complete': 1}
        items = self.search(query)
        if items:
            items = items[0]
            file_details = items.get('Pdf')
            file_url = file_details.get('download', '')
            response = self.get(file_url)
            if response and obj:
                filename = f'{obj.sample_id}_results.pdf'
                obj.upload_results_doc(content=response.content, filename=filename)

    def get_pcr_results(self, template_name='SARS COV 2 PCR'):
        portal_type = 'AnalysisRequest'
        client_uid = self.get_uid('Client', Title='AZD1222')
        results = []

        query = {
            'portal_type': portal_type,
            'getClientUID': client_uid,
            'complete': True,
            'limit': 9999,
            'review_state': 'published',
            'catalog': 'bika_catalog_analysisrequest_listing',
        }
        items = self.search(query)
        items = [sample for sample in items if sample.get('TemplateTitle') == template_name]

        for item in items:
            results_dict = {}
            subject_identifier = item.get('getParticipantID')
            subject_visit = item.get('getVisit').split('.')
            visit_code = subject_visit[0]
            visit_code_sequence = 0
            if len(subject_visit) > 1:
                visit_code_sequence = subject_visit[1]
            results_dict.update(subject_identifier=subject_identifier,
                                visit_code=visit_code,
                                visit_code_sequence=visit_code_sequence)
            if item.get('Analyses'):
                analyses = self.get_items(item.get('Analyses')[0].get('api_url'))
                if analyses:
                    result = self.result_mapping(analyses[0].get('Result'))
                    results_dict.update(covid_result=result)
            results.append(results_dict)
        return results

    def result_mapping(self, result):
        results_map = {'1': POS, '2': NEG, '3': IND}
        if result:
            return results_map.get(result)
        return None
