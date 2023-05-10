import pytz
import json
from datetime import datetime

from .api_resolvers_mixin import APIResolversMixin


class SampleImporter(APIResolversMixin):

    def create_sample(self, data=None):
        values = self.resolve_uids(data)

        # Create the Sample with JSON API
        client_uid = values.get('Client')
        slug = 'AnalysisRequest/create/{}'.format(client_uid)
        response = self.post(slug, values)
        result = json.loads(response.text)

        items = result.get('items', [])
        if items:
            id = items[0].get('id')
            print(f'Object created: {id}')
#             print(f'Transition sample {id} to Lab....')
#             transition_data = {'transition': 'send_to_lab'}
#             self.update_sample(identifier=id, data=transition_data)
#             print(f'Sample {id} successfully sent to lab')

        print(f'Total requests: {self._number_of_requests}')
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

        sample_uid = self.get_uid('AnalysisRequest', id=identifier)
        slug = f'AnalysisRequest/update/{sample_uid}'
        response = self.post(slug, values)
        result = json.loads(response.text)
        items = result.get('items', [])
        if items:
            id = items[0].get('id')
            print(f'Object updated: {id}')

        print(f'Total requests: {self._number_of_requests}')

    def resolve_uids(self, data):
        """Creates a Sample in SENAITE using the JSON API
        """
        # Get the uid of the client of the Sample
        client_uid = self.get_uid('Client', Title=data.get('Client'))

        # Get the uid of the Contact
        contact_uid = self.get_uid('Contact',
                                   getParentUID=client_uid,
                                   getFullname=data.get('Contact'))

        # Get the uid of the Sample type
        sample_type = data.get('SampleType')
        st_uid = self.get_uid('SampleType',
                              catalog='bika_setup_catalog',
                              conditional={'title': sample_type, 'Title': sample_type})

        # Resolve the container type uid
        ct_uid = self.get_uid('ContainerType',
                              catalog='bika_setup_catalog',
                              Title=data.get('DefaultContainerType'))

        # Resolve the uid of the Template
        at_uid = self.get_uid('ARTemplate',
                              catalog='bika_setup_catalog',
                              getClientUID=[client_uid, None],
                              title=data.get('Template'))

        courier_uid = self.get_uid(['Courier', 'ClientCourier'],
                                   getParentUID=client_uid,
                                   Title=data.get('Courier'))

        # Get the analyses from the temlate
        response = self.get(at_uid)
        template = json.loads(response.text)
        analyses = template.get('Analyses')
        analyses = map(lambda an: an.get('service_uid'), analyses)
        analyses = filter(None, analyses)

        # Replace object names by uids
        resolved_data = data.copy()
        resolved_data.update({
            'Client': client_uid,
            'Contact': contact_uid,
            'Courier': courier_uid,
            'DefaultContainerType': ct_uid,
            'SampleType': st_uid,
            'Template': at_uid,
            'Analyses': analyses,
        })
        return resolved_data
