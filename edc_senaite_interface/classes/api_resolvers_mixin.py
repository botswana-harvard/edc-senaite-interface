import json
import requests
from django.apps import apps as django_apps

app_config = django_apps.get_app_config('edc_senaite_interface')


class APIResolversMixin(object):

    session = None
    _number_of_requests = 0

    def __init__(self, host=None):
        self.host = host or app_config.host

    def auth(self, user, password):
        self.session = requests.Session()
        self.session.auth = (user, password)
        r = self.get('auth', None)
        return getattr(r, 'status_code', None) == 200

    def post(self, url, payload):
        url = self.resolve_api_slug(url)
        response = self.session.post(url, data=payload)
        print(f'{response.url}')
        self._number_of_requests += 1
        if response.status_code != 200:
            print(f'{response.status_code}')
        return response

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
                return []
                print(f'{response.status_code}')
            return response

    def get_uid(self, portal_type, **kwargs):
        items = None
        query = {
            'portal_type': portal_type
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
            print('No object found')
            return None
        if len(items) > 1:
            print('More than one object found')
            return None
        return items[0].get('uid')

    def resolve_api_slug(self, url):
        if self.host not in url:
            api_slug = 'senaite/@@API/senaite/v1'
            url = f'{self.host}/{api_slug}/{url}'
        return url

    def search(self, query):
        items = self.get_items('search', payload=query)
        return items or []

    def get_items(self, url, payload=None):
        r = self.get(url, payload=payload)
        if r.status_code != 200:
            return []
        data = json.loads(r.text)
        return data.get('items', [])
