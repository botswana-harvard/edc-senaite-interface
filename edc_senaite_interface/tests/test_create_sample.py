from django.test import TestCase
from datetime import datetime
from django.core.exceptions import ValidationError

from ..classes import SampleImporter
from ..models import SenaiteUser


class TestSendMessage(TestCase):

    def setUp(self):
        self.host = "https://lims-test.bhp.org.bw"
        self.user = "testing"
        self.password = "admin"

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
