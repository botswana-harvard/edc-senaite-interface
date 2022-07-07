import requests
from ..models import SenaiteUser
from django.apps import apps as django_apps
import json
from edc_constants.constants import POS, NEG, IND

app_config = django_apps.get_app_config('edc_senaite_interface')


class AnalysisResult(object):

    session = None
    _number_of_requests = 0

    def __init__(self, host=None):
        self.host = host or app_config.host

    def auth(self, user, password):
        self.session = requests.Session()
        self.session.auth = (user, password)
        r = self.get("auth")
        return r.status_code == 200

    @property
    def senaite_username(self):
        """Returns a senaite username.
        """
        try:
            senaite_user = SenaiteUser.objects.get(
                Q(username=self.user_created) | Q(username=self.user_modified))
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
                Q(username=self.user_created) | Q(username=self.user_modified))
        except SenaiteUser.DoesNotExist:
            pass
        else:
            return senaite_user.password

    def get(self, url, payload=None):
        url = self.resolve_api_slug(url)
        response = self.session.get(url, params=payload)
        print(f'{response.url}')
        self._number_of_requests += 1
        if response.status_code != 200:
            print(f'{response.status_code}')
        return response

    def post(self, url, payload):
        url = self.resolve_api_slug(url)
        response = self.session.post(url, data=payload)
        print(f'{response.url}')
        self._number_of_requests += 1
        if response.status_code != 200:
            print(f'{response.status_code}')
        return response

    def resolve_api_slug(self, url):
        if self.host not in url:
            api_slug = "senaite/@@API/senaite/v1"
            url = f"{self.host}/{api_slug}/{url}"
        return url

    def get_uid(self, portal_type, **kwargs):
        query = {
            "portal_type": portal_type
        }
        if kwargs:
            query.update(**kwargs)
        items = self.search(query)
        if not items:
            print("No object found")
            return None
        if len(items) > 1:
            print("More than one object found")
            return None
        return items[0].get("uid")

    def search(self, query):
        items = self.get_items("search", payload=query)
        return items or []

    def get_items(self, url, payload=None):
        r = self.get(url, payload=payload)
        if r.status_code != 200:
            return []
        data = json.loads(r.text)
        return data.get("items")

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

#     def requistion_identifiers(self):
#         subject_identifiers = []
#         requisition_cls = django_apps.get_model(
#             'esr21_subject.subjectrequisition')
#         requisitions = requisition_cls.objects.filter(
#             panel__name='sars_cov2_pcr').values_list(
#             'subject_visit__subject_identifier', flat=True)
#         print(requisitions)
