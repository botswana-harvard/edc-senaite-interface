from django.test import TestCase, tag
from datetime import datetime
from django.core.exceptions import ValidationError
from edc_senaite_interface.classes.get_results import AnalysisResult

from ..classes import SampleImporter
from ..models import SenaiteUser


class TestSendMessage(TestCase):

    def setUp(self):
        self.host = "https://bhplims.bhp.org.bw"
        self.user = "admin"
        self.password = "gah+w2Tu"

        SenaiteUser.objects.create(
            username='testing',
            contact='Test Contact',
            password='admin')

        self.data = {
            "Client": "TESTING",
            "Contact": "Test Contact",
            "Courier": "Test Courier",
            "SampleType": "Whole Blood EDTA",
            "DateSampled": datetime.now().strftime("%Y-%m-%d %H:%M"), # "2020-07-02 14:21:20",
            "Template": "HIV RNA PCR",
            "DefaultContainerType": "EDTA tube",
            # Fields specific from BHP
            "ParticipantID": "12342342333",
            "ParticipantInitials": "CK",
            "Gender": "m",
            "Visit": 2,
            "VisitCode": "screening",
            "DateOfBirth": "1978-11-03",
            "Volume": "10mL",
        }

    def test_create_sample(self):
        """
        """
        importer = SampleImporter(host=self.host)
        if importer.auth(self.user, self.password):
            importer.create_sample(data=self.data)
        else:
            raise ValidationError('Cannot authenticate')

    @tag('get_results')
    def test_get_results(self):
        analysis_request = AnalysisResult(host=self.host)
        if analysis_request.auth(self.user, self.password):
            analysis_request.get_results()
        else:
            raise ValidationError('Cannot authenticate')

    @tag('get_requsitions')
    def test_get_requisitions(self):
        analysis_request = AnalysisResult(host=self.host)
        print(analysis_request.requistion_identifiers())
