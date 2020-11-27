from django.test import TestCase
from datetime import datetime

from ..classes import SampleImporter
from ..models import SenaiteUser


class TestSendMessage(TestCase):

    def setUp(self):
        self.host = "http://localhost:8080"
        self.user = "ckgathi"
        self.password = "thabo321"
    
        senaite_user = SenaiteUser.objects.create(
            username='ckgathi',
            contact='Coulson Kgathi',
            password='thabo321')
    
        requisition_options = {}
    
        self.data = {
            "Client": "IMPAACT 1093 Molepolole",
            "Contact": "Gaerolwe Masheto",
            "SampleType": "Plasma EDTA",
            "DateSampled": datetime.now().strftime("%Y-%m-%d %H:%M"), # "2020-07-02 14:21:20",
            "Template": "PBMC/PL STORAGE",
            "DefaultContainerType": "EDTA Tube",
            # Fields specific from BHP
            "ParticipantID": "11111111111111111111",
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
            print("Cannot authenticate")

    def test_create_sample_using_requisition(self):
        """Test create sample on LIS using requisition.
        """
        pass

