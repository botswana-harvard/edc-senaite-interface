import configparser

from django.apps import apps as django_apps
from django.conf import settings
from django.core.management.base import BaseCommand
from requests import ConnectionError

from ...classes import AnalysisResult


app_config = django_apps.get_app_config('edc_senaite_interface')


class Command(BaseCommand):
    """Usage:
        python manage.py pull_results --sample_ids=`01123AAA01, `
    """

    help = ('Pull results from the senaite LIS into the EDC.')

    def add_arguments(self, parser):
        parser.add_argument(
            '--sample_ids',
            dest='sample_ids',
            help=('Only pull results for given sample identifiers. Accepts a '
                  'comma-separated list of IDs.'),
        )

    def handle(self, *args, **options):
        sids = options['sample_ids']
        result_models = getattr(app_config, 'result_models', {})
        if sids:
            sample_ids = [sid.strip() for sid in sids.split(',')]
        else:
            sample_ids = []
        for app_label, models in result_models.items():
            result_model = f'{app_label}.{models[0]}'
            result_value_model = f'{app_label}.{models[1]}'
            for sid in sample_ids:
                self.pull_results(sample_id=sid, result_model=result_model,
                                  result_value_model=result_value_model)

    def pull_results(self, sample_id=None, result_model=None, result_value_model=None):
        """ Connect to the senaite API and pull results for the specific sample
            ID provided.
            @param sample_id: ID of a specific sample
            @param result_model: `app_label.result_model_name` for a specific app
            @param result_value_model: `app_label.result_model_name` for a specific app
        """
        analysis = AnalysisResult(host=app_config.host, result_model=result_model,
                                  result_value_model=result_value_model)
        username = self.credentials.get('super_user', '')
        password = self.credentials.get('password', '')
        try:
            authenticated = analysis.auth(username, password)
        except ConnectionError:
            print("Cannot authenticate")
        else:
            if authenticated:
                analysis.get_sample_results(sample_id=sample_id, )

    @property
    def credentials(self):
        """ Create a dictionary with senaite super user credential info.
        @return: credentials
        """
        credentials = {}
        config = configparser.ConfigParser()

        settings_dict = settings.SENAITE_CONFIGURATION
        config_file = settings_dict['OPTIONS'].get('read_default_file')
        config.read(config_file)
        if config_file:
            credentials.update(super_user=config['read']['admin_user'],
                               password=config['read']['admin_password'])
        return credentials
