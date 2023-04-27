import pytz
import requests
import json
from datetime import datetime

from django.apps import apps as django_apps

app_config = django_apps.get_app_config('edc_senaite_interface')


class SampleImporter(object):

    session = None
    _number_of_requests = 0

    def __init__(self, host=None):
        self.host = host or app_config.host

    def create_sample(self, data=None):
        values = self.resolve_uids(data)

        # Create the Sample with JSON API
        client_uid = values.get("Client")
        slug = "AnalysisRequest/create/{}".format(client_uid)
        response = self.post(slug, values)
        result = json.loads(response.text)

        items = result.get("items")
        if items:
            id = items[0].get("id")
            print(f"Object created: {id}")
#             print(f'Transition sample {id} to Lab....')
#             transition_data = {'transition': 'send_to_lab'}
#             self.update_sample(identifier=id, data=transition_data)
#             print(f'Sample {id} successfully sent to lab')

        print("Total requests: {self._number_of_requests}")
        return response

    def update_sample(self, identifier=None, data=None):
        values = data
        if 'transition' not in data.keys():
            values = self.resolve_uids(data)

            # Cannot update client, sample type and template... unauthorized.
            exclude = ['Client', 'SampleType', 'Template', 'Analyses']
            for value in exclude:
                values.pop(value)
        sampled_dt = datetime.strptime(values.get('DateSampled'), "%Y-%m-%d %H:%M")
        values.update({'DateSampled':  sampled_dt.astimezone(pytz.UTC)})

        sample_uid = self.get_uid("AnalysisRequest", id=identifier)
        slug = f'AnalysisRequest/update/{sample_uid}'
        response = self.post(slug, values)
        result = json.loads(response.text)
        items = result.get("items")
        if items:
            id = items[0].get("id")
            print(f"Object updated: {id}")

        print("Total requests: {self._number_of_requests}")

    def resolve_uids(self, data):
        """Creates a Sample in SENAITE using the JSON API
        """
        # Get the uid of the client of the Sample
        client_uid = self.get_uid("Client", Title=data.get('Client'))

        # Get the uid of the Contact
        contact_uid = self.get_uid("Contact",
                                   getParentUID=client_uid,
                                   getFullname=data.get('Contact'))

        # Get the uid of the Sample type
        sample_type = data.get('SampleType')
        st_uid = self.get_uid("SampleType",
                              catalog="bika_setup_catalog",
                              conditional={'title': sample_type, 'Title': sample_type})

        # Resolve the container type uid
        ct_uid = self.get_uid("ContainerType",
                              catalog="bika_setup_catalog",
                              Title=data.get('DefaultContainerType'))

        # Resolve the uid of the Template
        at_uid = self.get_uid("ARTemplate",
                              catalog="bika_setup_catalog",
                              getClientUID=[client_uid, None],
                              title=data.get('Template'))

        courier_uid = self.get_uid(["Courier", "ClientCourier"],
                                   getParentUID=client_uid,
                                   Title=data.get('Courier'))

        # Get the analyses from the temlate
        response = self.get(at_uid)
        template = json.loads(response.text)
        analyses = template.get("Analyses")
        analyses = map(lambda an: an.get("service_uid"), analyses)
        analyses = filter(None, analyses)

        # Replace object names by uids
        resolved_data = data.copy()
        resolved_data.update({
            "Client": client_uid,
            "Contact": contact_uid,
            "Courier": courier_uid,
            "DefaultContainerType": ct_uid,
            "SampleType": st_uid,
            "Template": at_uid,
            "Analyses": analyses,
        })
        return resolved_data

    def get_uid(self, portal_type, **kwargs):
        items = None
        query = {
            "portal_type": portal_type
        }

        if kwargs:
            conditional = kwargs.pop('conditional', {})
            query.update(**kwargs)

            if not conditional:
                items = self.search(query)

            for key, value in conditional.items():
                query.update({f'{key}': value})

                items = self.search(query)
                if items:
                    break
                query.pop(key)
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

    def get(self, url, payload=None):
        url = self.resolve_api_slug(url)
        try:
            response = self.session.get(url, params=payload)
        except requests.ConnectionError:
            raise
        else:
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

    def auth(self, user, password):
        self.session = requests.Session()
        self.session.auth = (user, password)
        r = self.get("auth")
        return r.status_code == 200

    def resolve_api_slug(self, url):
        if self.host not in url:
            api_slug = "senaite/@@API/senaite/v1"
            url = f"{self.host}/{api_slug}/{url}"
        return url
