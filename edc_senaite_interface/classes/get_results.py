import requests
from ..models import SenaiteUser
from django.apps import apps as django_apps
import json

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

    def get_results(self):
        portal_type = 'AnalysisRequest'
        client_uid = self.get_uid("Client", Title='AZD1222')
        # search = 'AZD1222'
        query = {
            'portal_type': portal_type,
            'getClientUID': client_uid,
            'catalog': 'bika_catalog_analysisrequest_listing',
            'limit': 9999,
            'getParticipantID': '150-040990805-8',
            'review_state': 'published'
        }
        items = self.search(query)
        for item in items:
            sample_uid = item['uid']
            url = f'analysisrequest/{sample_uid}'
            analyses_requests = self.get_items(url)
            for analyses_request in analyses_requests:
                analyses = analyses_request['Analyses']
                for analys in analyses:
                    results = self.get_items(analys['api_url'])
                    for result in results:
                        if result['ShortTitle'] == 'SARS-CoV-2':
                            analysis_result_options = result['ResultOptions']
                            print(analysis_result_options)
                            analysis_result = result['Result']
                            result_mapping = self.result_mapping(
                                analysis_result, analysis_result_options)
                            print(result_mapping)
        # client = self.resolve_api_slug(f'search?portal_type=AnalysisRequest&getClientUID={client_uid}')
        # client = self.get_items(client)
        return items

    def result_mapping(self, result, result_options=None):
        for option in result_options:
            if option['ResultValue'] == result:
                return option['ResultText']
        return None

    def requistion_identifiers(self):
        subject_identifiers = []
        requisition_cls = django_apps.get_model(
            'esr21_subject.subjectrequisition')
        requisitions = requisition_cls.objects.filter(
            panel__name='sars_cov2_pcr').values_list(
            'subject_visit__subject_identifier', flat=True)
        print(requisitions)
