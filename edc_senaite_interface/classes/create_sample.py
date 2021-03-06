import requests
import json

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

        print("Total requests: {self._number_of_requests}")

    def resolve_uids(self, data):
        """Creates a Sample in SENAITE using the JSON API
        """
        # Get the uid of the client of the Sample
        client_uid = self.get_uid("Client", Title=data["Client"])

        # Get the uid of the Contact
        contact_uid = self.get_uid("Contact",
                                   getParentUID=client_uid,
                                   getFullname=data["Contact"])

        # Get the uid of the Sample type
        st_uid = self.get_uid("SampleType",
                              catalog="bika_setup_catalog",
                              Title=data["SampleType"])

        # Resolve the container type uid
        ct_uid = self.get_uid("ContainerType",
                              catalog="bika_setup_catalog",
                              Title=data["DefaultContainerType"])

        # Resolve the uid of the Template
        at_uid = self.get_uid("ARTemplate",
                              catalog="bika_setup_catalog",
                              getClientUID=[client_uid, None],
                              title=data["Template"])

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
            "SampleType": st_uid,
            "DefaultContainerType": ct_uid,
            "Template": at_uid,
            "Analyses": analyses,
        })
        return resolved_data

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
